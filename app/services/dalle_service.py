"""
DALL-E Service

Handles image generation for alibi support images, reaction images,
and photo-based alibi image generation.
"""

import base64
from openai import AsyncOpenAI

from ..config import get_settings
from ..schemas.message import AlibiImageRequest, PhotoBasedAlibiRequest, PhotoAnalysisResult
from ..schemas.response import AlibiImageResponse
from ..schemas.reaction_image import (
    ReactionImageRequest,
    ReactionImageResponse,
    ReactionStyle,
)
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

    async def generate_reaction_image(
        self, request: ReactionImageRequest
    ) -> ReactionImageResponse:
        """
        Generate an emotion-based reaction image.

        Creates an expressive image suitable for use as a chat reaction.
        """
        # Generate optimized prompt
        prompt = SystemPromptGenerator.generate_reaction_image_prompt(
            emotion=request.emotion.value,
            style=request.style.value,
            context=request.message_context,
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

        # Get usage suggestion
        suggested_usage = SystemPromptGenerator.get_emotion_usage_suggestion(
            request.emotion.value
        )

        # Generate alternative prompts for regeneration
        alternative_prompts = self._generate_alternative_prompts(
            request.emotion.value, request.style.value
        )

        return ReactionImageResponse(
            image_url=image_url,
            emotion=request.emotion.value,
            style=request.style.value,
            prompt_used=prompt,
            suggested_usage=suggested_usage,
            alternative_prompts=alternative_prompts,
        )

    def _generate_alternative_prompts(
        self,
        emotion: str,
        current_style: str
    ) -> list[str]:
        """Generate alternative prompts for different styles."""
        alternatives = []
        other_styles = [
            s.value for s in ReactionStyle
            if s.value != current_style
        ][:3]  # Get up to 3 alternative styles

        for style in other_styles:
            alt_prompt = SystemPromptGenerator.generate_reaction_image_prompt(
                emotion=emotion,
                style=style,
                context=None,
            )
            alternatives.append(alt_prompt)

        return alternatives

    # ============================================================
    # PHOTO-BASED ALIBI IMAGE GENERATION
    # ============================================================

    async def analyze_photo(
        self,
        image_base64: str,
        image_type: str = "jpeg"
    ) -> PhotoAnalysisResult:
        """
        Analyze an uploaded photo using GPT-4 Vision.

        Extracts person description, clothing, and suggests alibi scenarios.
        Note: Does not identify faces, only describes general appearance.
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 사진 분석 전문가입니다.
사진 속 인물의 외형적 특징을 분석해주세요.

주의사항:
- 얼굴 인식이나 신원 확인은 하지 마세요
- 일반적인 외형 특징만 설명하세요 (체형, 헤어스타일, 의상 등)
- 개인정보 보호를 위해 구체적인 얼굴 특징은 제외하세요

JSON 형식으로 응답:
{
    "person_description": "인물의 일반적인 외형 설명",
    "clothing_description": "의상 및 스타일 설명",
    "suggested_scenarios": ["추천 알리바이 상황1", "추천 상황2", "추천 상황3"]
}"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 사진 속 인물의 외형과 스타일을 분석해주세요. 이 스타일에 어울리는 알리바이 상황도 추천해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return PhotoAnalysisResult(
            person_description=result.get("person_description", ""),
            clothing_description=result.get("clothing_description", ""),
            suggested_scenarios=result.get("suggested_scenarios", []),
        )

    async def generate_photo_based_alibi(
        self,
        photo_analysis: PhotoAnalysisResult,
        request: PhotoBasedAlibiRequest,
    ) -> AlibiImageResponse:
        """
        Generate an alibi image based on photo analysis.

        Creates a new image that matches the person's style/appearance
        in the specified alibi scenario.
        """
        # Build detailed prompt based on photo analysis and request
        prompt = self._build_photo_based_prompt(photo_analysis, request)

        # Generate image with DALL-E
        response = await self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Generate tips
        tips = self._generate_photo_alibi_tips(request)

        return AlibiImageResponse(
            image_url=image_url,
            prompt_used=prompt,
            situation=request.situation,
            usage_tips=tips,
        )

    def _build_photo_based_prompt(
        self,
        analysis: PhotoAnalysisResult,
        request: PhotoBasedAlibiRequest,
    ) -> str:
        """Build a detailed prompt for photo-based alibi generation."""
        # Base prompt
        prompt_parts = [
            "A realistic smartphone photo of a person",
            f"with the following appearance: {analysis.person_description}",
            f"wearing: {analysis.clothing_description}",
        ]

        # Add situation
        prompt_parts.append(f"The person is {request.situation}.")

        # Add location if specified
        if request.location:
            prompt_parts.append(f"Location: {request.location}.")

        # Add time of day lighting
        if request.time_of_day:
            time_lighting = {
                "morning": "soft morning light, golden hour",
                "afternoon": "bright daylight, natural lighting",
                "evening": "warm evening light, sunset colors",
                "night": "indoor lighting, night time ambiance",
            }
            lighting = time_lighting.get(request.time_of_day, "natural lighting")
            prompt_parts.append(f"Lighting: {lighting}.")

        # Add activity
        if request.activity:
            prompt_parts.append(f"Activity: {request.activity}.")

        # Add style
        if request.style == "realistic":
            prompt_parts.append("Style: photorealistic, candid smartphone photo, casual composition, authentic feel.")
        else:
            prompt_parts.append("Style: artistic, slightly stylized but believable.")

        # Safety: avoid generating identifiable faces
        prompt_parts.append("The person should be shown from behind, side profile, or with face partially obscured naturally (looking at phone, drinking coffee, etc.) for privacy.")

        return " ".join(prompt_parts)

    def _generate_photo_alibi_tips(self, request: PhotoBasedAlibiRequest) -> list[str]:
        """Generate tips specific to photo-based alibi images."""
        tips = [
            "생성된 이미지는 AI가 만든 것이므로 실제 사진과 다를 수 있습니다.",
            "이미지의 메타데이터(EXIF)는 포함되지 않으니 참고하세요.",
            "자연스러운 상황 설명과 함께 사용하세요.",
        ]

        if request.time_of_day:
            tips.append(f"'{request.time_of_day}' 시간대에 맞게 메시지를 보내세요.")

        if request.location:
            tips.append(f"'{request.location}' 관련 디테일을 대화에 포함하세요.")

        return tips
