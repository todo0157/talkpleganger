"""
Alibi Mode Router

Endpoints for 1:N announcements, alibi image generation, and tone-based announcements.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional

from ..schemas.message import AlibiModeRequest, AlibiImageRequest, ChatToneAnalysis, ToneBasedAnnouncementRequest
from ..schemas.response import AlibiMessageResponse, AlibiImageResponse
from ..services.gpt_service import GPTService
from ..services.dalle_service import DalleService
from ..services.kakao_parser import KakaoParser

router = APIRouter(prefix="/alibi", tags=["Alibi Mode"])


@router.post(
    "/announce",
    response_model=AlibiMessageResponse,
    summary="Generate 1:N announcements",
    description="Generate group-tailored messages from a single announcement.",
)
async def generate_alibi_announcements(request: AlibiModeRequest):
    """
    Generate multiple versions of an announcement for different groups.

    This endpoint takes a single core message and adapts it for
    different recipient groups with appropriate tones:

    - Formal for work colleagues
    - Casual for friends
    - Respectful for family elders
    - Intimate for close ones

    Each group receives a message tailored to the relationship dynamics.

    Example use cases:
    - Announcing a schedule change to multiple groups
    - Sending event invitations with different tones
    - Coordinating alibis across different social circles
    """
    gpt_service = GPTService()
    response = await gpt_service.generate_alibi_messages(request=request)

    return response


@router.post(
    "/image",
    response_model=AlibiImageResponse,
    summary="Generate alibi support image",
    description="Generate a realistic image to support an alibi story using DALL-E 3.",
)
async def generate_alibi_image(request: AlibiImageRequest):
    """
    Generate a realistic alibi support image using DALL-E 3.

    This endpoint creates convincing images depicting various situations:
    - Working late at the office
    - Meeting at a cafe
    - Stuck in traffic
    - At a study session
    - Visiting a friend

    The images are generated to look like authentic smartphone photos.

    **Important Notes:**
    - Images are AI-generated and should be used responsibly
    - Consider the ethical implications of your use case
    - Generated images do not contain location metadata
    """
    dalle_service = DalleService()
    response = await dalle_service.generate_alibi_image(request=request)

    return response


@router.post(
    "/quick-announce",
    response_model=AlibiMessageResponse,
    summary="Quick 1:N announcement",
    description="Simplified endpoint for common announcement scenarios.",
)
async def quick_announce(
    user_id: str,
    announcement: str,
    include_groups: list[str] = None,
):
    """
    Quick announcement generator with preset groups.

    Default groups:
    - work: Formal tone for colleagues
    - friends: Casual tone for friends
    - family: Respectful tone for family

    Specify which groups to include or leave empty for all.
    """
    from ..schemas.message import RecipientGroup

    # Default groups
    all_groups = {
        "work": RecipientGroup(
            group_id="work",
            group_name="직장 동료",
            tone="formal",
        ),
        "friends": RecipientGroup(
            group_id="friends",
            group_name="친구들",
            tone="casual",
        ),
        "family": RecipientGroup(
            group_id="family",
            group_name="가족",
            tone="polite",
        ),
    }

    # Select groups
    if include_groups:
        selected_groups = []
        for group_id in include_groups:
            if group_id in all_groups:
                selected_groups.append(all_groups[group_id])
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown group: {group_id}. Available: {list(all_groups.keys())}",
                )
    else:
        selected_groups = list(all_groups.values())

    # Create request
    request = AlibiModeRequest(
        user_id=user_id,
        announcement=announcement,
        groups=selected_groups,
    )

    # Generate messages
    gpt_service = GPTService()
    response = await gpt_service.generate_alibi_messages(request=request)

    return response


# ============================================================
# Tone Analysis Endpoints
# ============================================================

@router.post(
    "/analyze-tone",
    response_model=ChatToneAnalysis,
    summary="Analyze chat tone from KakaoTalk file",
    description="Upload a KakaoTalk chat file to analyze the tone and style.",
)
async def analyze_chat_tone(
    file: UploadFile = File(...),
    my_name: str = Form(default="나"),
):
    """
    Analyze the tone of a KakaoTalk chat export file.

    This endpoint extracts linguistic features from the chat:
    - Formality level (formal/casual/intimate)
    - Emoji usage patterns
    - Common expressions and phrases
    - Sentence ending styles (요/ㅋㅋ/임/등)

    Use this analysis to generate announcements matching the chat's style.
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="txt 파일만 지원됩니다.",
        )

    try:
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일이 비어있습니다.",
            )

        # Parse chat file
        examples, parse_result = KakaoParser.parse_from_bytes(
            content=content,
            my_name=my_name,
            max_examples=100,  # More examples for better analysis
        )

        if not parse_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parse_result.error_message,
            )

        if len(examples) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="톤 분석을 위해 최소 5개의 메시지가 필요합니다.",
            )

        # Analyze tone using GPT
        gpt_service = GPTService()
        tone_analysis = await gpt_service.analyze_chat_tone(examples)

        return tone_analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"톤 분석 중 오류가 발생했습니다: {str(e)}",
        )


@router.post(
    "/announce-with-tone",
    summary="Generate announcement matching chat tone",
    description="Generate an announcement that matches the analyzed chat tone.",
)
async def announce_with_tone(request: ToneBasedAnnouncementRequest):
    """
    Generate an announcement that matches the analyzed chat tone.

    The announcement will:
    - Use the same formality level as the chat
    - Include similar emoji patterns
    - Use common expressions from the chat
    - Match sentence ending styles
    """
    gpt_service = GPTService()
    result = await gpt_service.generate_tone_based_announcement(request)
    return result
