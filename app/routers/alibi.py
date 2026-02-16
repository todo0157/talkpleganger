"""
Alibi Mode Router

Endpoints for 1:N announcements and alibi image generation.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.message import AlibiModeRequest, AlibiImageRequest
from ..schemas.response import AlibiMessageResponse, AlibiImageResponse
from ..services.gpt_service import GPTService
from ..services.dalle_service import DalleService

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
