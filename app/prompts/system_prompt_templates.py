"""
System Prompt Templates for Talk-pleganger

This module contains the core logic for generating system prompts
that enable GPT to mimic user personas based on few-shot examples.
"""

from typing import Optional
from ..schemas.persona import PersonaProfile, ChatExample, RecipientPersona
from ..schemas.message import RecipientGroup


class SystemPromptGenerator:
    """Generates system prompts for different operational modes."""

    # ============================================================
    # PERSONA ANALYSIS PROMPT
    # ============================================================
    PERSONA_ANALYSIS_PROMPT = """당신은 언어학 전문가입니다. 다음 대화 예시들을 분석하여 사용자의 말투 특성을 JSON 형식으로 추출해주세요.

분석할 대화 예시:
{chat_examples}

다음 형식으로 분석 결과를 반환해주세요:
{{
    "sentence_length": "short/medium/long",
    "honorific_level": "formal/polite/casual/intimate",
    "emoji_usage": "none/rare/moderate/frequent",
    "tone": "formal/friendly/playful/serious",
    "special_expressions": ["자주 사용하는 표현1", "자주 사용하는 표현2"],
    "analysis_summary": "전체적인 말투 특성 요약"
}}"""

    # ============================================================
    # AUTO MODE SYSTEM PROMPT TEMPLATE (WITH EMOTION ANALYSIS)
    # ============================================================
    AUTO_MODE_TEMPLATE = """당신은 사용자의 카카오톡 메시지를 대신 작성하는 AI 어시스턴트입니다.
상대방의 감정을 분석하고, 그에 맞게 톤을 조절하여 응답합니다.

## 사용자 프로필
- 이름: {user_name}
- 문장 길이: {sentence_length}
- 높임말 수준: {honorific_level}
- 이모지 사용: {emoji_usage}
- 전체적인 톤: {tone}
- 자주 쓰는 표현: {special_expressions}

## 사용자의 실제 대화 예시 (Few-shot Learning)
아래 예시들을 참고하여 사용자의 말투를 정확히 모방해주세요:

{few_shot_examples}

## 감정 분석 및 톤 조절 가이드
상대방 메시지의 감정을 먼저 분석하고, 아래 가이드에 따라 톤을 조절하세요:

| 감정 | 권장 톤 조절 |
|------|-------------|
| happy (기쁨) | 함께 기뻐하며 긍정적으로 |
| sad (슬픔) | 공감하며 위로하는 톤으로 |
| angry (화남) | 차분하고 이해하는 톤으로, 방어적이지 않게 |
| anxious (불안) | 안심시키며 지지하는 톤으로 |
| excited (흥분) | 열정적으로 함께 호응 |
| neutral (중립) | 평소 말투 유지 |
| confused (혼란) | 명확하고 친절하게 설명 |
| grateful (감사) | 겸손하게 받아들이며 |
| apologetic (미안함) | 관대하게, 괜찮다고 안심시키며 |
| urgent (긴급) | 간결하고 핵심만, 빠르게 |

## 지시사항
1. 먼저 상대방 메시지의 감정을 분석하세요.
2. 감정에 맞게 톤을 조절하되, 사용자의 기본 말투는 유지하세요.
3. 위 예시의 말투, 어조, 표현 방식을 최대한 따라해주세요.
4. 자연스럽고 인간적인 답변을 생성하세요.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요:
{{
    "answer": "생성된 답장 메시지",
    "confidence_score": 0.0~1.0 사이의 신뢰도 점수,
    "detected_intent": "상대 메시지의 의도 분석",
    "suggested_alternatives": ["대안 답장1", "대안 답장2"],
    "emotion_analysis": {{
        "primary_emotion": "happy/sad/angry/anxious/excited/neutral/confused/grateful/apologetic/urgent 중 하나",
        "emotion_intensity": 0.0~1.0 (감정 강도),
        "emotion_keywords": ["감정을 나타내는 키워드들"],
        "recommended_tone": "권장 응답 톤",
        "tone_adjustment": "톤 조절 내용 설명"
    }}
}}"""

    # ============================================================
    # ASSIST MODE SYSTEM PROMPT TEMPLATE
    # ============================================================
    ASSIST_MODE_TEMPLATE = """당신은 대인관계 커뮤니케이션 전문가입니다. 사용자가 특정 상대에게 보낼 메시지를 작성하는 것을 도와주세요.

## 상대방 정보
- 관계: {relationship}
- 나이대: {age_group}
- 성격/특성: {personality}
- 선호하는 소통 방식: {preferences}

## 상황
{situation}

## 사용자의 목표
{goal}

## 지시사항
1. 상대방의 특성과 관계를 고려한 적절한 메시지를 생성하세요.
2. 요청된 각 스타일(polite/logical/soft/humorous)에 맞는 변형을 제공하세요.
3. 각 변형에 대해 톤 설명과 위험도 평가를 포함하세요.
4. 상황에 맞는 실용적인 커뮤니케이션 팁을 제공하세요.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요:
{{
    "situation_analysis": "상황 분석",
    "recommended_approach": "권장 접근 방식",
    "variations": [
        {{
            "style": "스타일명",
            "message": "생성된 메시지",
            "tone_description": "톤 설명",
            "risk_level": "low/medium/high"
        }}
    ],
    "tips": ["팁1", "팁2", "팁3"]
}}"""

    # ============================================================
    # ALIBI MODE - 1:N ANNOUNCEMENT TEMPLATE
    # ============================================================
    ALIBI_ANNOUNCEMENT_TEMPLATE = """당신은 메시지 톤 변환 전문가입니다. 하나의 공지/안내 메시지를 여러 그룹에 맞게 변환해주세요.

## 원본 공지
{announcement}

## 추가 맥락
{context}

## 대상 그룹들
{groups}

## 지시사항
1. 각 그룹의 특성과 관계에 맞게 메시지 톤을 조절하세요.
2. 핵심 내용은 유지하면서 표현 방식만 변경하세요.
3. 각 그룹에 적합한 인사말과 마무리를 사용하세요.
4. 메시지 전달 순서 제안도 포함하세요.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요:
{{
    "original_announcement": "원본 공지",
    "group_messages": [
        {{
            "group_id": "그룹ID",
            "group_name": "그룹명",
            "message": "변환된 메시지",
            "tone_used": "사용된 톤"
        }}
    ],
    "delivery_order_suggestion": ["그룹1", "그룹2", "그룹3"]
}}"""

    # ============================================================
    # ALIBI MODE - IMAGE PROMPT TEMPLATE
    # ============================================================
    ALIBI_IMAGE_PROMPT_TEMPLATE = """Create a realistic, convincing photo that depicts the following situation:

Situation: {situation}
Style: {style}
Additional details: {additional_details}

Requirements:
- The image should look natural and authentic, like a real photo taken with a smartphone
- Include realistic lighting and environment details
- No text or watermarks in the image
- The scene should be believable and mundane

Generate a detailed, natural-looking scene."""

    # ============================================================
    # FOLLOW-UP MODE TEMPLATE
    # ============================================================
    FOLLOWUP_MODE_TEMPLATE = """당신은 대화 전문가입니다. 상대방이 읽고 답장하지 않았을 때 자연스럽게 대화를 이어갈 수 있는 후속 메시지를 생성해주세요.

## 사용자 프로필
- 이름: {user_name}
- 말투 톤: {tone}
- 이모지 사용: {emoji_usage}

## 상황
- 마지막 보낸 메시지: {last_message}
- 경과 시간: {hours_elapsed}시간
- 상대와의 관계: {relationship}
- 원래 의도: {original_intent}

## 후속 메시지 전략 가이드
| 경과 시간 | 전략 | 설명 |
|----------|------|------|
| 1-2시간 | gentle_reminder | 부드러운 리마인더, 추가 정보 제공 |
| 2-4시간 | casual_check | 가벼운 안부 또는 관련 질문 |
| 4-8시간 | conversation_starter | 새로운 화제로 자연스럽게 전환 |
| 8-24시간 | topic_change | 완전히 다른 주제로 새 대화 시작 |
| 24시간+ | reconnect | 시간이 지난 것을 자연스럽게 인정하며 다시 연결 |

## 지시사항
1. 사용자의 말투와 톤을 유지하면서 후속 메시지를 생성하세요.
2. 상대방을 압박하거나 불편하게 하지 않는 자연스러운 메시지를 만드세요.
3. 경과 시간에 따라 적절한 전략을 선택하세요.
4. 각 제안에 대해 위험도와 사용 적절 상황을 설명하세요.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요:
{{
    "recommended_strategy": "전략명 (gentle_reminder/casual_check/conversation_starter/topic_change/reconnect)",
    "strategy_explanation": "왜 이 전략이 좋은지",
    "suggestions": [
        {{
            "message": "후속 메시지",
            "strategy": "사용된 전략",
            "tone_description": "톤 설명",
            "risk_level": "low/medium/high",
            "recommended_for": "이 메시지를 사용하면 좋은 상황"
        }}
    ],
    "tips": ["팁1", "팁2", "팁3"],
    "should_wait_more": true/false,
    "recommended_additional_wait_hours": null 또는 숫자
}}"""

    # ============================================================
    # REACTION IMAGE PROMPT TEMPLATES
    # ============================================================
    REACTION_IMAGE_TEMPLATES = {
        "meme": """Create a funny meme-style reaction image expressing {emotion}.
Style: Internet meme, bold and expressive, humorous
Emotion keywords: {emotion_keywords}
Context: {context}
Requirements:
- Highly expressive facial expression or character
- Clean, shareable format suitable for messaging
- No offensive content
- Works well at small sizes for chat apps
- Bright, eye-catching colors""",

        "emoji_art": """Create a large emoji-style art illustration expressing {emotion}.
Style: Simplified, colorful, emoji-inspired digital illustration
Emotion: {emotion}
Requirements:
- Single expressive character or face filling most of the frame
- Bright, vibrant colors with clean edges
- Simple solid color or gradient background
- Instantly recognizable emotion
- Suitable for messaging apps like KakaoTalk""",

        "cute_character": """Create an adorable kawaii-style character reaction image expressing {emotion}.
Style: Kawaii, chibi, cute character illustration
Emotion: {emotion}
Context: {context}
Requirements:
- Adorable round character design with big eyes
- Exaggerated but cute emotional expression
- Soft, pastel colors preferred
- Appeal to Korean messaging culture
- Simple background that doesn't distract from character""",

        "sticker": """Create a messaging app sticker design expressing {emotion}.
Style: Clean sticker design with bold outlines, like KakaoTalk emoticons
Emotion: {emotion}
Requirements:
- Simple, clear design with defined edges
- Works well at small sizes (128x128 to 512x512)
- Expressive without needing text
- White or transparent-friendly background
- Suitable for Korean messaging apps""",

        "minimal": """Create a minimal line art illustration expressing {emotion}.
Style: Minimalist line art, modern and clean
Emotion: {emotion}
Requirements:
- Simple geometric shapes and clean lines
- Limited color palette (2-3 colors maximum)
- Modern, sophisticated aesthetic
- Subtle but clearly recognizable emotion
- White or simple background""",
    }

    EMOTION_KEYWORDS = {
        "happy": ["joyful", "smiling", "cheerful", "bright", "delighted", "grinning"],
        "sad": ["melancholy", "tearful", "downcast", "blue", "dejected", "crying"],
        "angry": ["frustrated", "annoyed", "fierce", "intense", "fuming", "mad"],
        "surprised": ["shocked", "amazed", "wide-eyed", "startled", "astonished"],
        "love": ["heart-eyes", "affectionate", "adoring", "sweet", "loving", "hearts"],
        "tired": ["exhausted", "sleepy", "drained", "yawning", "weary", "drowsy"],
        "confused": ["puzzled", "questioning", "uncertain", "head-tilted", "perplexed"],
        "excited": ["enthusiastic", "jumping", "energetic", "thrilled", "pumped"],
        "grateful": ["thankful", "appreciative", "touched", "moved", "blessed"],
        "apologetic": ["sorry", "regretful", "sheepish", "guilty", "remorseful"],
    }

    EMOTION_USAGE_SUGGESTIONS = {
        "happy": "좋은 소식에 반응하거나 축하할 때 사용하세요",
        "sad": "공감하거나 슬픈 상황을 표현할 때 사용하세요",
        "angry": "짜증나는 상황에 공감을 표현할 때 사용하세요",
        "surprised": "놀라운 소식이나 예상치 못한 상황에 사용하세요",
        "love": "감사하거나 애정을 표현할 때 사용하세요",
        "tired": "피곤하거나 지친 상황을 표현할 때 사용하세요",
        "confused": "이해가 안 되거나 당황스러운 상황에 사용하세요",
        "excited": "기대되거나 흥분되는 상황에 사용하세요",
        "grateful": "감사를 표현하거나 고마움을 전할 때 사용하세요",
        "apologetic": "미안함을 표현하거나 사과할 때 사용하세요",
    }

    @classmethod
    def format_chat_examples(cls, examples: list[ChatExample]) -> str:
        """Format chat examples for prompt inclusion."""
        formatted = []
        for i, ex in enumerate(examples, 1):
            role_label = "나" if ex.role == "user" else "상대방"
            formatted.append(f"예시 {i}:\n{role_label}: {ex.content}")
        return "\n\n".join(formatted)

    @classmethod
    def format_few_shot_examples(cls, examples: list[ChatExample]) -> str:
        """Format examples as few-shot conversation pairs."""
        formatted = []
        # Group into pairs (other's message -> user's response)
        current_context = None
        for ex in examples:
            if ex.role == "other":
                current_context = ex.content
            elif ex.role == "user" and current_context:
                formatted.append(
                    f"상대방: {current_context}\n나의 답장: {ex.content}"
                )
                current_context = None
            elif ex.role == "user":
                formatted.append(f"나의 메시지: {ex.content}")
        return "\n\n".join(formatted)

    @classmethod
    def generate_persona_analysis_prompt(
        cls, chat_examples: list[ChatExample]
    ) -> str:
        """Generate a prompt for analyzing user's persona from chat examples."""
        examples_str = cls.format_chat_examples(chat_examples)
        return cls.PERSONA_ANALYSIS_PROMPT.format(chat_examples=examples_str)

    @classmethod
    def generate_auto_mode_prompt(cls, persona: PersonaProfile) -> str:
        """Generate system prompt for Auto Mode based on user persona."""
        few_shot = cls.format_few_shot_examples(persona.chat_examples)
        special_expr = ", ".join(persona.special_expressions) if persona.special_expressions else "없음"

        return cls.AUTO_MODE_TEMPLATE.format(
            user_name=persona.name,
            sentence_length=persona.sentence_length,
            honorific_level=persona.honorific_level,
            emoji_usage=persona.emoji_usage,
            tone=persona.tone,
            special_expressions=special_expr,
            few_shot_examples=few_shot,
        )

    @classmethod
    def generate_assist_mode_prompt(
        cls,
        recipient: RecipientPersona,
        situation: str,
        goal: str,
    ) -> str:
        """Generate system prompt for Assist Mode."""
        return cls.ASSIST_MODE_TEMPLATE.format(
            relationship=recipient.relationship.value,
            age_group=recipient.age_group or "알 수 없음",
            personality=recipient.personality or "특별한 정보 없음",
            preferences=recipient.preferences or "특별한 선호 없음",
            situation=situation,
            goal=goal,
        )

    @classmethod
    def generate_alibi_announcement_prompt(
        cls,
        announcement: str,
        groups: list[RecipientGroup],
        context: Optional[str] = None,
    ) -> str:
        """Generate system prompt for Alibi 1:N announcement mode."""
        groups_str = "\n".join(
            [f"- {g.group_name} (ID: {g.group_id}): 톤 - {g.tone}" for g in groups]
        )
        return cls.ALIBI_ANNOUNCEMENT_TEMPLATE.format(
            announcement=announcement,
            context=context or "추가 맥락 없음",
            groups=groups_str,
        )

    @classmethod
    def generate_alibi_image_prompt(
        cls,
        situation: str,
        style: str = "realistic",
        additional_details: Optional[str] = None,
    ) -> str:
        """Generate DALL-E prompt for alibi image generation."""
        return cls.ALIBI_IMAGE_PROMPT_TEMPLATE.format(
            situation=situation,
            style=style,
            additional_details=additional_details or "None",
        )

    @classmethod
    def generate_followup_prompt(
        cls,
        persona: PersonaProfile,
        last_message: str,
        hours_elapsed: float,
        relationship: str,
        original_intent: Optional[str] = None,
    ) -> str:
        """Generate prompt for follow-up message generation."""
        return cls.FOLLOWUP_MODE_TEMPLATE.format(
            user_name=persona.name,
            tone=persona.tone,
            emoji_usage=persona.emoji_usage,
            last_message=last_message,
            hours_elapsed=hours_elapsed,
            relationship=relationship,
            original_intent=original_intent or "특별한 의도 없음",
        )

    @classmethod
    def generate_reaction_image_prompt(
        cls,
        emotion: str,
        style: str = "cute_character",
        context: Optional[str] = None,
    ) -> str:
        """Generate DALL-E prompt for reaction image generation."""
        template = cls.REACTION_IMAGE_TEMPLATES.get(
            style, cls.REACTION_IMAGE_TEMPLATES["cute_character"]
        )
        emotion_keywords = ", ".join(
            cls.EMOTION_KEYWORDS.get(emotion, ["expressive"])
        )
        return template.format(
            emotion=emotion,
            emotion_keywords=emotion_keywords,
            context=context or "general chat reaction",
        )

    @classmethod
    def get_emotion_usage_suggestion(cls, emotion: str) -> str:
        """Get usage suggestion for a specific emotion."""
        return cls.EMOTION_USAGE_SUGGESTIONS.get(
            emotion, "다양한 상황에서 사용할 수 있습니다"
        )

    @classmethod
    def get_emotion_keywords(cls, emotion: str) -> list[str]:
        """Get keywords for a specific emotion."""
        return cls.EMOTION_KEYWORDS.get(emotion, ["expressive"])
