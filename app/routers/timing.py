"""
Timing Router

Endpoints for response timing analysis and recommendations.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, Form, Query

from ..schemas.timing import (
    TimingPattern,
    TimingRecommendation,
    UrgencyLevel,
)
from ..services.timing_service import TimingService
from ..services.persona_engine import PersonaEngine

router = APIRouter(prefix="/timing", tags=["Response Timing"])


@router.post(
    "/analyze",
    response_model=TimingPattern,
    summary="Analyze timing from KakaoTalk export",
    description="Extract response timing patterns from a KakaoTalk chat export file.",
)
async def analyze_timing_from_kakao(
    file: UploadFile,
    persona_id: str = Form(...),
    my_name: str = Form(default="나"),
):
    """
    Analyze timing patterns from a KakaoTalk export file.

    This endpoint:
    1. Parses the KakaoTalk chat file
    2. Extracts response time patterns
    3. Calculates statistics (avg, min, max)
    4. Analyzes patterns by time of day
    5. Saves the pattern for future recommendations

    Returns the analyzed timing pattern.
    """
    # Verify persona exists
    engine = PersonaEngine()
    persona = engine.get_persona(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona {persona_id} not found.",
        )

    # Read file content
    content = await file.read()

    # Try different encodings
    decoded_content = None
    for encoding in ["utf-8", "cp949", "euc-kr"]:
        try:
            decoded_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if not decoded_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode file. Please ensure it's a valid KakaoTalk export.",
        )

    # Analyze timing
    timing_service = TimingService()
    timing_data = timing_service.analyze_kakao_timing(decoded_content, my_name)

    if timing_data["sample_count"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract timing patterns. Ensure the file contains message timestamps.",
        )

    # Save pattern
    pattern = timing_service.save_timing_pattern(persona_id, timing_data)

    return pattern


@router.get(
    "/{persona_id}/recommend",
    response_model=TimingRecommendation,
    summary="Get timing recommendation",
    description="Get a response timing recommendation for a persona.",
)
async def get_timing_recommendation(
    persona_id: str,
    urgency: UrgencyLevel = Query(default=UrgencyLevel.MEDIUM),
    emotion: str = Query(default=None),
):
    """
    Get a timing recommendation for responding.

    Considers:
    - User's historical response patterns
    - Current time of day
    - Message urgency
    - Message emotion

    Returns a recommendation with confidence score.
    """
    # Verify persona exists
    engine = PersonaEngine()
    persona = engine.get_persona(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona {persona_id} not found.",
        )

    timing_service = TimingService()
    recommendation = timing_service.recommend_timing(
        persona_id=persona_id,
        message_emotion=emotion,
        urgency=urgency,
    )

    return recommendation


@router.get(
    "/{persona_id}/patterns",
    response_model=TimingPattern,
    summary="Get timing patterns",
    description="Get stored timing patterns for a persona.",
)
async def get_timing_patterns(persona_id: str):
    """
    Get the stored timing patterns for a persona.

    Returns the analyzed patterns including:
    - Average response time
    - Min/max response times
    - Time of day variations
    """
    # Verify persona exists
    engine = PersonaEngine()
    persona = engine.get_persona(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona {persona_id} not found.",
        )

    timing_service = TimingService()
    pattern = timing_service.get_timing_pattern(persona_id)

    if not pattern:
        # Return default pattern
        return TimingPattern(
            persona_id=persona_id,
            avg_response_minutes=5.0,
            min_response_minutes=1.0,
            max_response_minutes=30.0,
            time_of_day_patterns={},
            sample_count=0,
        )

    return pattern


@router.delete(
    "/{persona_id}/patterns",
    summary="Delete timing patterns",
    description="Delete all timing patterns for a persona.",
)
async def delete_timing_patterns(persona_id: str):
    """
    Delete all stored timing patterns for a persona.

    Use this to reset and re-analyze patterns.
    """
    timing_service = TimingService()
    deleted = timing_service.db.delete_timing_patterns(persona_id)

    return {
        "success": deleted,
        "message": f"Timing patterns for {persona_id} deleted." if deleted else "No patterns found.",
    }
