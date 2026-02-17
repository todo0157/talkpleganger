"""
Follow-up Router

Endpoints for generating follow-up messages when there's no response.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.followup import (
    FollowUpRequest,
    FollowUpResponse,
    FollowUpStrategy,
)
from ..services.persona_engine import PersonaEngine
from ..services.gpt_service import GPTService

router = APIRouter(prefix="/followup", tags=["Follow-up Messages"])


@router.post(
    "/suggest",
    response_model=FollowUpResponse,
    summary="Generate follow-up suggestions",
    description="Generate natural follow-up messages for no-reply situations.",
)
async def suggest_followup(request: FollowUpRequest):
    """
    Generate follow-up message suggestions.

    This endpoint helps when someone hasn't replied by:
    1. Analyzing the elapsed time
    2. Considering the relationship
    3. Generating appropriate follow-up strategies
    4. Providing multiple message options

    Each suggestion includes:
    - The message text
    - Strategy used (gentle reminder, casual check, etc.)
    - Risk level assessment
    - Usage recommendation
    """
    # Get user's persona
    engine = PersonaEngine()
    persona = engine.get_persona(request.user_id)

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {request.user_id} not found. Please create a persona first.",
        )

    # Generate follow-up suggestions
    gpt_service = GPTService()
    response = await gpt_service.generate_followup_messages(
        persona=persona,
        request=request,
    )

    return response


@router.get(
    "/strategies",
    summary="List follow-up strategies",
    description="Get list of available follow-up strategies with descriptions.",
)
async def list_strategies():
    """
    List all available follow-up strategies.

    Each strategy is suited for different elapsed time periods:
    - gentle_reminder (1-2 hours)
    - casual_check (2-4 hours)
    - conversation_starter (4-8 hours)
    - topic_change (8-24 hours)
    - reconnect (24+ hours)
    """
    return {
        "strategies": [
            {
                "id": "gentle_reminder",
                "label": "부드러운 리마인더",
                "hours": "1-2시간",
                "description": "마지막 메시지에 추가 정보를 덧붙이거나 부드럽게 리마인드",
                "example": "아 그리고 내일까지 알려주면 좋을 것 같아!",
            },
            {
                "id": "casual_check",
                "label": "가벼운 안부",
                "hours": "2-4시간",
                "description": "가벼운 안부나 관련된 질문으로 대화 재개",
                "example": "바쁜가보다~ 언제 괜찮아?",
            },
            {
                "id": "conversation_starter",
                "label": "새 화제 전환",
                "hours": "4-8시간",
                "description": "자연스럽게 새로운 화제로 대화 전환",
                "example": "오 그거 그렇고 이거 봤어?",
            },
            {
                "id": "topic_change",
                "label": "주제 변경",
                "hours": "8-24시간",
                "description": "완전히 새로운 주제로 대화 시작",
                "example": "야 이번 주말 뭐해?",
            },
            {
                "id": "reconnect",
                "label": "다시 연결",
                "hours": "24시간+",
                "description": "시간이 지난 것을 인정하며 자연스럽게 재연결",
                "example": "아 맞다 어제 바빴구나! 오늘은 어때?",
            },
        ]
    }


@router.get(
    "/quick/{hours}",
    response_model=dict,
    summary="Quick strategy recommendation",
    description="Get a quick strategy recommendation based on elapsed hours.",
)
async def quick_strategy(hours: float):
    """
    Get a quick strategy recommendation based on elapsed time.

    Returns the most appropriate strategy for the given time period.
    """
    if hours < 1:
        return {
            "recommendation": "wait",
            "message": "아직 기다려보세요. 1시간 후에 다시 확인해보세요.",
            "wait_hours": 1 - hours,
        }
    elif hours < 2:
        strategy = FollowUpStrategy.GENTLE_REMINDER
        tip = "마지막 메시지에 자연스럽게 정보를 추가하세요."
    elif hours < 4:
        strategy = FollowUpStrategy.CASUAL_CHECK
        tip = "가벼운 안부나 관련 질문을 해보세요."
    elif hours < 8:
        strategy = FollowUpStrategy.CONVERSATION_STARTER
        tip = "새로운 화제로 자연스럽게 대화를 전환해보세요."
    elif hours < 24:
        strategy = FollowUpStrategy.TOPIC_CHANGE
        tip = "완전히 새로운 주제로 대화를 시작해보세요."
    else:
        strategy = FollowUpStrategy.RECONNECT
        tip = "시간이 지난 것을 인정하며 자연스럽게 재연결하세요."

    return {
        "recommendation": strategy.value,
        "elapsed_hours": hours,
        "tip": tip,
    }
