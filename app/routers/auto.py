"""
Auto Mode Router

Endpoints for automatic response generation in user's speaking style.
With context memory and timing recommendations.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.message import AutoModeRequest, IncomingMessage
from ..schemas.response import AutoModeResponse
from ..schemas.timing import UrgencyLevel
from ..services.persona_engine import PersonaEngine
from ..services.gpt_service import GPTService
from ..services.timing_service import TimingService
from ..storage import get_database

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
    2. Auto-fetches context from chat history (if enabled)
    3. Analyzes the incoming message
    4. Generates a response matching the user's linguistic patterns
    5. Provides timing recommendation (if enabled)
    6. Returns the response with confidence score and alternatives

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

    db = get_database()

    # Auto-fetch context if enabled and no context provided
    context_messages = request.context_messages
    context_used = 0

    if request.auto_fetch_context and not context_messages:
        # Fetch recent messages from database
        recent_messages = db.get_context_messages(
            user_id=request.user_id,
            sender_id=request.incoming_message.sender_id,
            limit=request.context_window_size,
        )
        # Convert to IncomingMessage format
        context_messages = [
            IncomingMessage(
                sender_id=msg.get("sender_id", ""),
                sender_name=msg.get("sender_name", ""),
                message_text=msg.get("message_text", ""),
            )
            for msg in recent_messages
            if msg.get("message_text")
        ]
        context_used = len(context_messages)

    # Generate response
    gpt_service = GPTService()
    response = await gpt_service.generate_auto_response(
        persona=persona,
        incoming_message=request.incoming_message,
        context_messages=context_messages,
        response_length=request.response_length,
    )

    # Save to chat history
    emotion = None
    emotion_intensity = None
    if response.emotion_analysis:
        emotion = response.emotion_analysis.primary_emotion.value
        emotion_intensity = response.emotion_analysis.emotion_intensity

    db.add_chat_message(
        user_id=request.user_id,
        sender_name=request.incoming_message.sender_name,
        sender_id=request.incoming_message.sender_id,
        message_text=request.incoming_message.message_text,
        response_text=response.answer,
        emotion=emotion,
        emotion_intensity=emotion_intensity,
        confidence_score=response.confidence_score,
    )

    # Generate timing recommendation if enabled
    timing_recommendation = None
    if request.include_timing:
        timing_service = TimingService()
        # Determine urgency from emotion
        urgency = UrgencyLevel.MEDIUM
        if emotion in ["urgent", "anxious"]:
            urgency = UrgencyLevel.HIGH
        elif emotion in ["happy", "grateful"]:
            urgency = UrgencyLevel.LOW

        timing = timing_service.recommend_timing(
            persona_id=request.user_id,
            message_emotion=emotion,
            urgency=urgency,
        )
        timing_recommendation = {
            "recommended_wait_minutes": timing.recommended_wait_minutes,
            "confidence": timing.confidence,
            "reason": timing.reason,
            "natural_range": timing.natural_range,
            "time_of_day": timing.time_of_day.value,
        }

    # Update response with additional info
    response.timing_recommendation = timing_recommendation
    response.context_used = context_used

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
