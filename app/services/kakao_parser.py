"""
KakaoTalk Chat Export Parser

Parses exported KakaoTalk chat txt files into structured chat examples.
Supports both 1:1 chats and group chats.
Handles multiple encodings (UTF-8, CP949, EUC-KR) automatically.
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass
from ..schemas.persona import ChatExample


@dataclass
class ParseResult:
    """Result of parsing attempt with detailed error info."""
    success: bool
    content: str = ""
    encoding_used: str = ""
    error_message: str = ""
    error_line: int = 0
    problematic_text: str = ""


class EncodingDetector:
    """Handles encoding detection and text normalization for KakaoTalk exports."""

    # Supported encodings in priority order
    ENCODINGS = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'utf-16', 'utf-16-le', 'utf-16-be']

    @classmethod
    def detect_and_decode(cls, content: bytes) -> ParseResult:
        """
        Detect encoding and decode content with detailed error reporting.

        Args:
            content: Raw bytes from uploaded file

        Returns:
            ParseResult with decoded text or detailed error info
        """
        if not content:
            return ParseResult(
                success=False,
                error_message="파일이 비어있습니다."
            )

        # Try each encoding
        last_error = ""
        for encoding in cls.ENCODINGS:
            try:
                decoded = content.decode(encoding)
                # Normalize line endings
                decoded = cls._normalize_line_endings(decoded)
                # Remove BOM if present
                decoded = cls._remove_bom(decoded)

                # Validate that it looks like a KakaoTalk export
                validation = cls._validate_kakao_format(decoded)
                if not validation[0]:
                    last_error = validation[1]
                    continue

                return ParseResult(
                    success=True,
                    content=decoded,
                    encoding_used=encoding
                )
            except UnicodeDecodeError as e:
                last_error = f"{encoding} 디코딩 실패: 위치 {e.start}-{e.end}"
                continue
            except Exception as e:
                last_error = str(e)
                continue

        # All encodings failed
        return ParseResult(
            success=False,
            error_message=f"파일 인코딩을 감지할 수 없습니다. {last_error}",
            problematic_text=cls._get_problematic_preview(content)
        )

    @classmethod
    def _normalize_line_endings(cls, text: str) -> str:
        """Normalize all line endings to \n."""
        return text.replace('\r\n', '\n').replace('\r', '\n')

    @classmethod
    def _remove_bom(cls, text: str) -> str:
        """Remove UTF-8 BOM if present."""
        if text.startswith('\ufeff'):
            return text[1:]
        return text

    @classmethod
    def _validate_kakao_format(cls, text: str) -> Tuple[bool, str]:
        """
        Validate that the text looks like a KakaoTalk export.

        Returns:
            Tuple of (is_valid, error_message)
        """
        lines = text.strip().split('\n')

        if len(lines) < 3:
            return False, "파일에 충분한 내용이 없습니다 (최소 3줄 필요)"

        # Check for KakaoTalk patterns
        kakao_patterns = [
            r'\[(오전|오후)\s*\d{1,2}:\d{2}\]',  # Time pattern
            r'님과 카카오톡 대화',  # Chat export header
            r'저장한 날짜',  # Save date
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',  # Date pattern
        ]

        found_pattern = False
        for line in lines[:20]:  # Check first 20 lines
            for pattern in kakao_patterns:
                if re.search(pattern, line):
                    found_pattern = True
                    break
            if found_pattern:
                break

        if not found_pattern:
            return False, "카카오톡 대화 내보내기 형식이 아닌 것 같습니다. 올바른 파일인지 확인해주세요."

        return True, ""

    @classmethod
    def _get_problematic_preview(cls, content: bytes) -> str:
        """Get a preview of problematic content for debugging."""
        try:
            # Try to decode with errors='replace' to show what we can
            preview = content[:200].decode('utf-8', errors='replace')
            return preview[:100] + "..." if len(preview) > 100 else preview
        except:
            return "(미리보기 불가)"


class KakaoParser:
    """Parser for KakaoTalk exported chat files."""

    # Pattern for chat messages: "이름 [오후/오전 시:분] 메시지"
    # Also handles variations like "이름 [오전 9:05]" or "이름 [오후 12:30]"
    MESSAGE_PATTERN = re.compile(
        r'^(.+?)\s+\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s+(.+)$'
    )

    # Alternative pattern for PC KakaoTalk export (slightly different format)
    MESSAGE_PATTERN_ALT = re.compile(
        r'^\[(.+?)\]\s+\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s+(.+)$'
    )

    # Pattern for date separators: "--- 2024년 1월 15일 ---" or "2024년 1월 15일 월요일"
    DATE_PATTERN = re.compile(r'^-*\s*\d{4}년\s*\d{1,2}월\s*\d{1,2}일.*-*$')

    # System messages to ignore
    SYSTEM_KEYWORDS = [
        '님이 들어왔습니다',
        '님이 나갔습니다',
        '님을 초대했습니다',
        '채팅방을 나갔습니다',
        '사진을 보냈습니다',
        '동영상을 보냈습니다',
        '파일을 보냈습니다',
        '이모티콘을 보냈습니다',
        '삭제된 메시지입니다',
        '님과 카카오톡 대화',
        '저장한 날짜',
        '채팅방 관리자가',
        '님이 나가셨습니다',
        '오픈채팅방',
    ]

    @classmethod
    def parse_from_bytes(
        cls,
        content: bytes,
        my_name: str = "나",
        max_examples: int = 50,
    ) -> Tuple[list[ChatExample], ParseResult]:
        """
        Parse KakaoTalk file from raw bytes with automatic encoding detection.

        Args:
            content: Raw bytes from uploaded file
            my_name: User's display name in the chat
            max_examples: Maximum number of examples to extract

        Returns:
            Tuple of (chat_examples, parse_result)
        """
        # Detect encoding and decode
        parse_result = EncodingDetector.detect_and_decode(content)

        if not parse_result.success:
            return [], parse_result

        # Parse the decoded content
        try:
            examples = cls.parse_chat_file(
                content=parse_result.content,
                my_name=my_name,
                max_examples=max_examples,
            )
            return examples, parse_result
        except Exception as e:
            parse_result.success = False
            parse_result.error_message = f"파싱 중 오류 발생: {str(e)}"
            return [], parse_result

    @classmethod
    def get_stats_from_bytes(cls, content: bytes) -> Tuple[dict, ParseResult]:
        """
        Get chat statistics from raw bytes with automatic encoding detection.

        Args:
            content: Raw bytes from uploaded file

        Returns:
            Tuple of (stats_dict, parse_result)
        """
        parse_result = EncodingDetector.detect_and_decode(content)

        if not parse_result.success:
            return {}, parse_result

        try:
            stats = cls.get_chat_stats(parse_result.content)
            return stats, parse_result
        except Exception as e:
            parse_result.success = False
            parse_result.error_message = f"통계 분석 중 오류 발생: {str(e)}"
            return {}, parse_result

    @classmethod
    def parse_chat_file(
        cls,
        content: str,
        my_name: str = "나",
        max_examples: int = 50,
    ) -> list[ChatExample]:
        """
        Parse KakaoTalk exported chat file content.
        Supports both 1:1 and group chats.

        Args:
            content: Raw text content from exported file
            my_name: User's display name in the chat (default: "나")
            max_examples: Maximum number of examples to extract

        Returns:
            List of ChatExample objects
        """
        lines = content.strip().split('\n')
        examples = []
        current_sender = None
        current_message = []

        # Normalize my_name for comparison
        my_name_normalized = my_name.strip().lower()

        for line in lines:
            line = line.strip()

            # Skip empty lines and date separators
            if not line or cls.DATE_PATTERN.match(line):
                continue

            # Try to match message pattern (mobile format first, then PC format)
            match = cls.MESSAGE_PATTERN.match(line)
            if not match:
                match = cls.MESSAGE_PATTERN_ALT.match(line)

            if match:
                # Save previous message if exists
                if current_sender is not None and current_message:
                    msg_text = ' '.join(current_message).strip()
                    if msg_text and not cls._is_system_message(msg_text):
                        # Check if this is user's message
                        sender_normalized = current_sender.strip().lower()
                        is_user = cls._is_my_message(sender_normalized, my_name_normalized)
                        role = "user" if is_user else "other"
                        examples.append(ChatExample(role=role, content=msg_text))

                # Start new message
                current_sender = match.group(1).strip()
                current_message = [match.group(5).strip()]
            else:
                # Continuation of previous message (multi-line)
                if current_sender is not None and line:
                    current_message.append(line)

        # Don't forget the last message
        if current_sender is not None and current_message:
            msg_text = ' '.join(current_message).strip()
            if msg_text and not cls._is_system_message(msg_text):
                sender_normalized = current_sender.strip().lower()
                is_user = cls._is_my_message(sender_normalized, my_name_normalized)
                role = "user" if is_user else "other"
                examples.append(ChatExample(role=role, content=msg_text))

        # Limit and balance examples
        return cls._balance_examples(examples, max_examples)

    @classmethod
    def _is_my_message(cls, sender: str, my_name: str) -> bool:
        """
        Check if the message is from the user.
        Uses flexible matching for various name formats.
        """
        # Exact match
        if sender == my_name:
            return True

        # Contains check (for nicknames)
        if my_name in sender or sender in my_name:
            return True

        # Check common Korean self-references
        common_self_names = ['나', '본인', '저']
        if sender in common_self_names and my_name in common_self_names:
            return True

        return False

    @classmethod
    def _is_system_message(cls, text: str) -> bool:
        """Check if message is a system notification."""
        return any(keyword in text for keyword in cls.SYSTEM_KEYWORDS)

    @classmethod
    def _balance_examples(
        cls,
        examples: list[ChatExample],
        max_count: int
    ) -> list[ChatExample]:
        """
        Balance examples to have roughly equal user/other messages.
        Prioritize conversation pairs (other -> user).
        """
        if len(examples) <= max_count:
            return examples

        # Try to keep conversation pairs
        balanced = []
        i = 0
        while i < len(examples) and len(balanced) < max_count:
            if examples[i].role == "other" and i + 1 < len(examples) and examples[i + 1].role == "user":
                # Keep the pair
                balanced.append(examples[i])
                balanced.append(examples[i + 1])
                i += 2
            else:
                balanced.append(examples[i])
                i += 1

        return balanced[:max_count]

    @classmethod
    def detect_participants(cls, content: str) -> dict:
        """
        Detect all participants in the chat.
        Returns dict with participant names and message counts.
        Useful for identifying who is who in group chats.
        Supports both mobile and PC export formats.
        """
        lines = content.strip().split('\n')
        participants = {}

        for line in lines:
            line_stripped = line.strip()
            # Try both mobile and PC patterns
            match = cls.MESSAGE_PATTERN.match(line_stripped)
            if not match:
                match = cls.MESSAGE_PATTERN_ALT.match(line_stripped)

            if match:
                sender = match.group(1).strip()
                if sender not in participants:
                    participants[sender] = 0
                participants[sender] += 1

        # Sort by message count (descending)
        return dict(sorted(participants.items(), key=lambda x: x[1], reverse=True))

    @classmethod
    def detect_my_name(cls, content: str) -> list[str]:
        """
        Detect possible user names from chat content.
        Returns list of unique sender names found, sorted by frequency.
        """
        participants = cls.detect_participants(content)
        return list(participants.keys())

    @classmethod
    def parse_group_chat(
        cls,
        content: str,
        my_name: str = "나",
        target_person: Optional[str] = None,
        max_examples: int = 50,
    ) -> list[ChatExample]:
        """
        Parse group chat with option to focus on specific person.

        Args:
            content: Raw text content
            my_name: User's display name
            target_person: If specified, only include conversations with this person
            max_examples: Maximum examples

        Returns:
            List of ChatExample objects
        """
        lines = content.strip().split('\n')
        examples = []
        current_sender = None
        current_message = []
        my_name_normalized = my_name.strip().lower()
        target_normalized = target_person.strip().lower() if target_person else None

        for line in lines:
            line = line.strip()

            if not line or cls.DATE_PATTERN.match(line):
                continue

            # Try both mobile and PC patterns
            match = cls.MESSAGE_PATTERN.match(line)
            if not match:
                match = cls.MESSAGE_PATTERN_ALT.match(line)

            if match:
                if current_sender is not None and current_message:
                    msg_text = ' '.join(current_message).strip()
                    if msg_text and not cls._is_system_message(msg_text):
                        sender_normalized = current_sender.strip().lower()
                        is_user = cls._is_my_message(sender_normalized, my_name_normalized)

                        # Filter by target person if specified
                        include_message = True
                        if target_normalized:
                            is_target = (
                                sender_normalized == target_normalized or
                                target_normalized in sender_normalized
                            )
                            include_message = is_user or is_target

                        if include_message:
                            role = "user" if is_user else "other"
                            examples.append(ChatExample(role=role, content=msg_text))

                current_sender = match.group(1).strip()
                current_message = [match.group(5).strip()]
            else:
                if current_sender is not None and line:
                    current_message.append(line)

        # Handle last message
        if current_sender is not None and current_message:
            msg_text = ' '.join(current_message).strip()
            if msg_text and not cls._is_system_message(msg_text):
                sender_normalized = current_sender.strip().lower()
                is_user = cls._is_my_message(sender_normalized, my_name_normalized)

                include_message = True
                if target_normalized:
                    is_target = (
                        sender_normalized == target_normalized or
                        target_normalized in sender_normalized
                    )
                    include_message = is_user or is_target

                if include_message:
                    role = "user" if is_user else "other"
                    examples.append(ChatExample(role=role, content=msg_text))

        return cls._balance_examples(examples, max_examples)

    @classmethod
    def get_chat_stats(cls, content: str) -> dict:
        """
        Get statistics about the chat.
        """
        participants = cls.detect_participants(content)
        total_messages = sum(participants.values())

        return {
            "total_messages": total_messages,
            "participant_count": len(participants),
            "participants": participants,
            "is_group_chat": len(participants) > 2,
        }
