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
)
from ..schemas.response import (
    AutoModeResponse,
    AssistModeResponse,
    ResponseVariation,
    AlibiMessageResponse,
    GroupMessage,
    EmotionAnalysis,
    EmotionType,
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
