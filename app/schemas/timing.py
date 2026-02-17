"""
Response Timing Schemas

Schemas for response timing analysis and recommendations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TimeOfDay(str, Enum):
    """Time of day categories."""
    EARLY_MORNING = "early_morning"  # 6-9
    MORNING = "morning"              # 9-12
    AFTERNOON = "afternoon"          # 12-18
    EVENING = "evening"              # 18-22
    NIGHT = "night"                  # 22-6


class UrgencyLevel(str, Enum):
    """Message urgency levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimingPattern(BaseModel):
    """Response timing pattern analysis result."""

    persona_id: str = Field(..., description="Persona ID")
    avg_response_minutes: float = Field(
        ..., description="Average response time in minutes"
    )
    min_response_minutes: float = Field(
        ..., description="Minimum response time in minutes"
    )
    max_response_minutes: float = Field(
        ..., description="Maximum response time in minutes"
    )
    time_of_day_patterns: dict[str, float] = Field(
        default_factory=dict,
        description="Average response time by time of day"
    )
    relationship_type: Optional[str] = Field(
        default=None, description="Relationship type for this pattern"
    )
    sample_count: int = Field(
        default=0, description="Number of samples analyzed"
    )


class TimingRecommendation(BaseModel):
    """Response timing recommendation."""

    recommended_wait_minutes: int = Field(
        ..., description="Recommended wait time in minutes"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    reason: str = Field(
        ..., description="Explanation for the recommendation"
    )
    time_of_day: TimeOfDay = Field(
        ..., description="Current time of day category"
    )
    urgency_level: UrgencyLevel = Field(
        default=UrgencyLevel.MEDIUM, description="Detected urgency level"
    )
    alternative_timings: list[dict] = Field(
        default_factory=list,
        description="Alternative timing suggestions"
    )
    natural_range: str = Field(
        default="", description="Natural response time range (e.g., '5-15분')"
    )


class TimingAnalysisRequest(BaseModel):
    """Request for timing analysis."""

    persona_id: str = Field(..., description="Persona ID to analyze")
    incoming_message_time: Optional[str] = Field(
        default=None, description="Time when the message was received"
    )
    sender_relationship: Optional[str] = Field(
        default=None, description="Relationship with the sender"
    )
    message_urgency: Optional[UrgencyLevel] = Field(
        default=None, description="Detected message urgency"
    )
    message_emotion: Optional[str] = Field(
        default=None, description="Detected message emotion"
    )
