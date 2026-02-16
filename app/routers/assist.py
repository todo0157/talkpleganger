"""
Assist Mode Router

Endpoints for guided response suggestions with multiple variations.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.message import AssistModeRequest
from ..schemas.response import AssistModeResponse
from ..services.persona_engine import PersonaEngine
from ..services.gpt_service import GPTService

router = APIRouter(prefix="/assist", tags=["Assist Mode"])


@router.post(
    "/suggest",
    response_model=AssistModeResponse,
    summary="Get response suggestions",
    description="Generate multiple response variations based on recipient persona.",
)
async def generate_assist_response(request: AssistModeRequest):
    """
    Generate multiple response variations for a given situation.

    This endpoint helps users communicate with:
    - Bosses and supervisors
    - Professors and mentors
    - Clients and business contacts
    - Family members with delicate relationships

    It provides:
    1. Situation analysis
    2. Recommended approach
    3. Multiple variations (Polite, Logical, Soft, etc.)
    4. Communication tips

    Each variation includes:
    - The message text
    - Tone description
    - Risk level assessment
    """
    # Optionally get user's persona for personalization
    engine = PersonaEngine()
    persona = engine.get_persona(request.user_id)

    # Generate variations
    gpt_service = GPTService()
    response = await gpt_service.generate_assist_response(
        request=request,
        persona=persona,  # May be None
    )

    return response


@router.post(
    "/quick-reply",
    response_model=AssistModeResponse,
    summary="Quick reply suggestions",
    description="Generate quick replies for common situations.",
)
async def generate_quick_reply(
    user_id: str,
    situation_type: str,
    recipient_relationship: str,
):
    """
    Generate quick reply suggestions for common situations.

    Supported situation_type values:
    - vacation_request: Requesting time off
    - deadline_extension: Asking for more time
    - meeting_reschedule: Changing meeting time
    - apology: Apologizing for a mistake
    - thank_you: Expressing gratitude
    - decline_politely: Politely declining a request

    This is a simplified endpoint for common use cases.
    """
    from ..schemas.persona import RecipientPersona, RelationshipType
    from ..schemas.message import VariationStyle

    # Map common situations to goals
    situation_goals = {
        "vacation_request": ("휴가를 요청하는 상황", "휴가 승인을 받고 싶습니다"),
        "deadline_extension": ("마감 연장을 요청하는 상황", "마감 기한을 연장받고 싶습니다"),
        "meeting_reschedule": ("회의 일정 변경을 요청하는 상황", "회의 시간을 조정하고 싶습니다"),
        "apology": ("실수에 대해 사과하는 상황", "진심어린 사과를 전달하고 싶습니다"),
        "thank_you": ("감사를 표현하는 상황", "진심어린 감사를 전달하고 싶습니다"),
        "decline_politely": ("요청을 정중히 거절하는 상황", "상대방 기분 상하지 않게 거절하고 싶습니다"),
    }

    if situation_type not in situation_goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown situation_type: {situation_type}. Supported: {list(situation_goals.keys())}",
        )

    situation, goal = situation_goals[situation_type]

    # Parse relationship
    try:
        relationship = RelationshipType(recipient_relationship)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown relationship: {recipient_relationship}. Supported: {[r.value for r in RelationshipType]}",
        )

    # Create request
    request = AssistModeRequest(
        user_id=user_id,
        recipient=RecipientPersona(relationship=relationship),
        situation=situation,
        goal=goal,
        variation_styles=[VariationStyle.POLITE, VariationStyle.LOGICAL, VariationStyle.SOFT],
    )

    # Generate response
    gpt_service = GPTService()
    response = await gpt_service.generate_assist_response(request=request)

    return response
