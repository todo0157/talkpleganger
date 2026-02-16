"""
KakaoTalk Chat Export Parser

Parses exported KakaoTalk chat txt files into structured chat examples.
Supports both 1:1 chats and group chats.
"""

import re
from typing import Optional
from ..schemas.persona import ChatExample


class KakaoParser:
    """Parser for KakaoTalk exported chat files."""

    # Pattern for chat messages: "이름 [오후/오전 시:분] 메시지"
    MESSAGE_PATTERN = re.compile(
        r'^(.+?)\s+\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s+(.+)$'
    )

    # Pattern for date separators: "--- 2024년 1월 15일 ---"
    DATE_PATTERN = re.compile(r'^-+\s*\d{4}년.*-+$')

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
    ]

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

            # Try to match message pattern
            match = cls.MESSAGE_PATTERN.match(line)

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
        """
        lines = content.strip().split('\n')
        participants = {}

        for line in lines:
            match = cls.MESSAGE_PATTERN.match(line.strip())
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

            match = cls.MESSAGE_PATTERN.match(line)

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
