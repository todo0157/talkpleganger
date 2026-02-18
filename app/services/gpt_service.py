"""
GPT Service

Handles all GPT API interactions for the three operational modes.
"""

import json
from typing import Optional
from openai import AsyncOpenAI

from ..config import get_settings
from ..schemas.persona import PersonaProfile, RecipientPersona
from ..schemas.message import (
    IncomingMessage,
    AssistModeRequest,
    AlibiModeRequest,
    RecipientGroup,
    ChatToneAnalysis,
    ToneBasedAnnouncementRequest,
)
from ..schemas.persona import ChatExample
from ..schemas.response import (
    AutoModeResponse,
    AssistModeResponse,
    ResponseVariation,
    AlibiMessageResponse,
    GroupMessage,
    EmotionAnalysis,
    EmotionType,
)
from ..schemas.followup import (
    FollowUpRequest,
    FollowUpResponse,
    FollowUpSuggestion,
    FollowUpStrategy,
)
from ..prompts import SystemPromptGenerator


class GPTService:
    """Service for GPT-powered response generation."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.max_response_tokens
        self.temperature = settings.temperature

    # ============================================================
    # AUTO MODE
    # ============================================================
    async def generate_auto_response(
        self,
        persona: PersonaProfile,
        incoming_message: IncomingMessage,
        context_messages: list[IncomingMessage] = None,
        response_length: Optional[str] = None,
    ) -> AutoModeResponse:
        """
        Generate an automatic response in the user's style.

        Uses the persona's system prompt with few-shot examples
        to generate a response that mimics the user's speaking style.
        """
        # Build conversation context
        messages = [
            {"role": "system", "content": persona.system_prompt},
        ]

        # Add context messages if provided
        if context_messages:
            for msg in context_messages[-5:]:  # Last 5 messages for context
                role = "assistant" if msg.sender_id == persona.user_id else "user"
                messages.append({"role": role, "content": msg.message_text})

        # Add the incoming message
        user_content = f"상대방({incoming_message.sender_name})의 메시지: {incoming_message.message_text}"
        if response_length:
            user_content += f"\n\n요청: {response_length} 길이로 답장해줘."
        messages.append({"role": "user", "content": user_content})

        # Call GPT API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)

        # Parse emotion analysis if present
        emotion_data = result.get("emotion_analysis")
        emotion_analysis = None
        if emotion_data:
            try:
                emotion_analysis = EmotionAnalysis(
                    primary_emotion=EmotionType(emotion_data.get("primary_emotion", "neutral")),
                    emotion_intensity=float(emotion_data.get("emotion_intensity", 0.5)),
                    emotion_keywords=emotion_data.get("emotion_keywords", []),
                    recommended_tone=emotion_data.get("recommended_tone", ""),
                    tone_adjustment=emotion_data.get("tone_adjustment", ""),
                )
            except (ValueError, KeyError):
                # Fallback if emotion parsing fails
                emotion_analysis = EmotionAnalysis(
                    primary_emotion=EmotionType.NEUTRAL,
                    emotion_intensity=0.5,
                    emotion_keywords=[],
                    recommended_tone="평소 말투 유지",
                    tone_adjustment="기본 톤 사용",
                )

        return AutoModeResponse(
            answer=result.get("answer", ""),
            confidence_score=float(result.get("confidence_score", 0.8)),
            detected_intent=result.get("detected_intent"),
            suggested_alternatives=result.get("suggested_alternatives", []),
            emotion_analysis=emotion_analysis,
        )

    # ============================================================
    # ASSIST MODE
    # ============================================================
    async def generate_assist_response(
        self,
        request: AssistModeRequest,
        persona: Optional[PersonaProfile] = None,
    ) -> AssistModeResponse:
        """
        Generate multiple response variations for a given situation.

        Provides different styles (polite, logical, soft, etc.)
        tailored to the recipient's persona and the user's goal.
        """
        # Generate system prompt
        system_prompt = SystemPromptGenerator.generate_assist_mode_prompt(
            recipient=request.recipient,
            situation=request.situation,
            goal=request.goal,
        )

        # Build user message
        user_content = f"다음 스타일로 메시지 변형을 생성해주세요: {', '.join([s.value for s in request.variation_styles])}"

        if request.incoming_message:
            user_content += f"\n\n상대방 메시지: {request.incoming_message.message_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # Call GPT API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens * 2,  # More tokens for multiple variations
            temperature=self.temperature,
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)

        variations = [
            ResponseVariation(
                style=v.get("style", "unknown"),
                message=v.get("message", ""),
                tone_description=v.get("tone_description", ""),
                risk_level=v.get("risk_level", "low"),
            )
            for v in result.get("variations", [])
        ]

        return AssistModeResponse(
            situation_analysis=result.get("situation_analysis", ""),
            recommended_approach=result.get("recommended_approach", ""),
            variations=variations,
            tips=result.get("tips", []),
        )

    # ============================================================
    # ALIBI MODE - 1:N Announcement
    # ============================================================
    async def generate_alibi_messages(
        self,
        request: AlibiModeRequest,
    ) -> AlibiMessageResponse:
        """
        Generate group-tailored messages from a single announcement.

        Takes one core message and adapts it for different groups
        with appropriate tones (formal for work, casual for friends, etc.)
        """
        # Generate system prompt
        system_prompt = SystemPromptGenerator.generate_alibi_announcement_prompt(
            announcement=request.announcement,
            groups=request.groups,
            context=request.context,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "각 그룹에 맞는 메시지를 생성해주세요."},
        ]

        # Call GPT API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens * 2,
            temperature=self.temperature,
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)

        group_messages = [
            GroupMessage(
                group_id=gm.get("group_id", ""),
                group_name=gm.get("group_name", ""),
                message=gm.get("message", ""),
                tone_used=gm.get("tone_used", ""),
            )
            for gm in result.get("group_messages", [])
        ]

        return AlibiMessageResponse(
            original_announcement=result.get("original_announcement", request.announcement),
            group_messages=group_messages,
            delivery_order_suggestion=result.get("delivery_order_suggestion", []),
        )

    # ============================================================
    # FOLLOW-UP MODE
    # ============================================================
    async def generate_followup_messages(
        self,
        persona: PersonaProfile,
        request: FollowUpRequest,
    ) -> FollowUpResponse:
        """
        Generate follow-up messages for no-reply situations.

        Suggests natural ways to continue the conversation
        based on elapsed time and relationship.
        """
        # Generate system prompt
        system_prompt = SystemPromptGenerator.generate_followup_prompt(
            persona=persona,
            last_message=request.last_message_text,
            hours_elapsed=request.hours_elapsed,
            relationship=request.recipient_relationship,
            original_intent=request.original_intent,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "적절한 후속 메시지를 생성해주세요."},
        ]

        # Call GPT API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens * 2,
            temperature=self.temperature,
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)

        # Parse suggestions
        suggestions = []
        for s in result.get("suggestions", []):
            try:
                strategy = FollowUpStrategy(s.get("strategy", "casual_check"))
            except ValueError:
                strategy = FollowUpStrategy.CASUAL_CHECK

            suggestions.append(FollowUpSuggestion(
                message=s.get("message", ""),
                strategy=strategy,
                tone_description=s.get("tone_description", ""),
                risk_level=s.get("risk_level", "low"),
                recommended_for=s.get("recommended_for", ""),
            ))

        # Parse recommended strategy
        try:
            recommended_strategy = FollowUpStrategy(
                result.get("recommended_strategy", "casual_check")
            )
        except ValueError:
            recommended_strategy = FollowUpStrategy.CASUAL_CHECK

        return FollowUpResponse(
            elapsed_hours=request.hours_elapsed,
            recommended_strategy=recommended_strategy,
            strategy_explanation=result.get("strategy_explanation", ""),
            suggestions=suggestions,
            tips=result.get("tips", []),
            should_wait_more=result.get("should_wait_more", False),
            recommended_additional_wait_hours=result.get("recommended_additional_wait_hours"),
        )

    # ============================================================
    # TONE ANALYSIS
    # ============================================================
    async def analyze_chat_tone(
        self,
        chat_examples: list[ChatExample],
    ) -> ChatToneAnalysis:
        """
        Analyze the tone of chat messages to extract linguistic features.

        Returns analysis of:
        - Formality level
        - Emoji usage patterns
        - Common expressions
        - Sentence ending styles
        """
        # Build examples text
        examples_text = "\n".join([
            f"[{ex.role}] {ex.content}"
            for ex in chat_examples[:50]  # Limit to 50 examples
        ])

        system_prompt = """당신은 한국어 언어학 전문가입니다. 주어진 카카오톡 대화를 분석하여 대화방의 톤과 스타일을 추출하세요.

분석 항목:
1. formality_level: 격식 수준 (formal/semi-formal/casual/intimate)
2. emoji_usage: 이모지 사용 빈도 (none/minimal/moderate/heavy)
3. common_expressions: 자주 사용하는 표현들 (최대 5개)
4. sentence_endings: 자주 사용하는 문장 끝맺음 (예: ~요, ~ㅋㅋ, ~임, ~ㅇㅇ, ~네 등)
5. overall_tone: 전체적인 톤 설명 (1-2문장)
6. recommended_style: 이 대화방에 공지를 보낼 때 추천하는 스타일 (1문장)

결과를 JSON 형식으로 반환하세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 대화를 분석해주세요:\n\n{examples_text}"},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)

        return ChatToneAnalysis(
            formality_level=result.get("formality_level", "casual"),
            emoji_usage=result.get("emoji_usage", "moderate"),
            common_expressions=result.get("common_expressions", []),
            sentence_endings=result.get("sentence_endings", []),
            overall_tone=result.get("overall_tone", ""),
            recommended_style=result.get("recommended_style", ""),
        )

    async def generate_tone_based_announcement(
        self,
        request: ToneBasedAnnouncementRequest,
    ) -> dict:
        """
        Generate an announcement that matches the analyzed chat tone.

        Uses the tone analysis to generate a message that fits naturally
        in the target chat room.
        """
        tone = request.tone_analysis

        system_prompt = f"""당신은 카카오톡 메시지 작성 전문가입니다.
주어진 공지 내용을 대화방의 톤에 맞게 변환해주세요.

대화방 톤 분석:
- 격식 수준: {tone.formality_level}
- 이모지 사용: {tone.emoji_usage}
- 자주 쓰는 표현: {', '.join(tone.common_expressions)}
- 문장 끝맺음 스타일: {', '.join(tone.sentence_endings)}
- 전체적인 톤: {tone.overall_tone}
- 추천 스타일: {tone.recommended_style}

위 톤에 맞춰 공지를 자연스럽게 작성해주세요.
결과를 JSON 형식으로 반환하세요:
{{
    "generated_message": "생성된 메시지",
    "tone_matched": true/false,
    "style_notes": "적용된 스타일 설명",
    "alternative_version": "다른 버전의 메시지 (선택)"
}}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 공지를 변환해주세요:\n\n{request.announcement}"},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.7,
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "original_announcement": request.announcement,
            "generated_message": result.get("generated_message", ""),
            "tone_matched": result.get("tone_matched", True),
            "style_notes": result.get("style_notes", ""),
            "alternative_version": result.get("alternative_version"),
            "group_name": request.group_name,
            "tone_analysis_summary": {
                "formality": tone.formality_level,
                "emoji_usage": tone.emoji_usage,
                "overall_tone": tone.overall_tone,
            },
        }
