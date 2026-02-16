"""
Auto Mode Router

Endpoints for automatic response generation in user's speaking style.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.message import AutoModeRequest
from ..schemas.response import AutoModeResponse
from ..services.persona_engine import PersonaEngine
from ..services.gpt_service import GPTService

router = APIRouter(prefix="/auto", tags=["Auto Mode"])


@router.post(
    "/respond",
    response_model=AutoModeResponse,
    summary="Generate automatic response",
    description="Generate a response in the user's speaking style.",
)
async def generate_auto_response(request: AutoModeRequest):
    """
    Generate an automatic response mimicking the user's speaking style.

    This endpoint:
    1. Retrieves the user's persona profile
    2. Analyzes the incoming message
    3. Generates a response matching the user's linguistic patterns
    4. Returns the response with confidence score and alternatives

    The response is formatted for easy integration with KakaoTalk.
    """
    # Get user's persona
    engine = PersonaEngine()
    persona = engine.get_persona(request.user_id)

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {request.user_id} not found. Please create a persona first.",
        )

    # Generate response
    gpt_service = GPTService()
    response = await gpt_service.generate_auto_response(
        persona=persona,
        incoming_message=request.incoming_message,
        context_messages=request.context_messages,
        response_length=request.response_length,
    )

    return response


@router.post(
    "/webhook",
    response_model=AutoModeResponse,
    summary="KakaoTalk webhook endpoint",
    description="Receive and auto-respond to KakaoTalk messages.",
)
async def kakao_webhook(request: AutoModeRequest):
    """
    Webhook endpoint for KakaoTalk message notifications.

    This endpoint is designed to receive forwarded messages from:
    - Android Notification Listener
    - Kakao Business Channel webhook

    It automatically generates and returns a response.
    In production, this would also handle message sending.
    """
    # Same logic as generate_auto_response
    engine = PersonaEngine()
    persona = engine.get_persona(request.user_id)

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {request.user_id} not found.",
        )

    gpt_service = GPTService()
    response = await gpt_service.generate_auto_response(
        persona=persona,
        incoming_message=request.incoming_message,
        context_messages=request.context_messages,
        response_length=request.response_length,
    )

    # TODO: In production, send the response back to KakaoTalk
    # kakao_service.send_message(
    #     recipient=request.incoming_message.sender_id,
    #     message=response.answer
    # )

    return response
