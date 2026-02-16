"""
DALL-E Service

Handles image generation for alibi support images.
"""

from openai import AsyncOpenAI

from ..config import get_settings
from ..schemas.message import AlibiImageRequest
from ..schemas.response import AlibiImageResponse
from ..prompts import SystemPromptGenerator


class DalleService:
    """Service for DALL-E image generation."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_dalle_model

    async def generate_alibi_image(
        self, request: AlibiImageRequest
    ) -> AlibiImageResponse:
        """
        Generate an alibi support image using DALL-E.

        Creates a realistic image depicting the specified situation
        to support the user's alibi story.
        """
        # Generate optimized prompt
        prompt = SystemPromptGenerator.generate_alibi_image_prompt(
            situation=request.situation,
            style=request.style,
            additional_details=request.additional_details,
        )

        # Call DALL-E API
        response = await self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Generate usage tips based on situation
        tips = self._generate_usage_tips(request.situation)

        return AlibiImageResponse(
            image_url=image_url,
            prompt_used=prompt,
            situation=request.situation,
            usage_tips=tips,
        )

    def _generate_usage_tips(self, situation: str) -> list[str]:
        """Generate contextual tips for using the alibi image."""
        base_tips = [
            "이미지를 보내기 전에 메타데이터(EXIF)를 확인하세요.",
            "상황에 맞는 시간대에 이미지를 보내세요.",
            "이미지와 함께 자연스러운 메시지를 추가하세요.",
        ]

        # Add situation-specific tips
        if "cafe" in situation.lower() or "카페" in situation:
            base_tips.append("카페 메뉴나 음료와 관련된 대화를 준비하세요.")
        elif "office" in situation.lower() or "회사" in situation or "사무실" in situation:
            base_tips.append("업무 관련 맥락을 준비하세요.")
        elif "restaurant" in situation.lower() or "식당" in situation:
            base_tips.append("음식이나 분위기에 대한 코멘트를 준비하세요.")

        return base_tips
