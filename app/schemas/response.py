from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .timing import TimingRecommendation


class EmotionType(str, Enum):
    """Detected emotion types."""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    GRATEFUL = "grateful"
    APOLOGETIC = "apologetic"
    URGENT = "urgent"


class EmotionAnalysis(BaseModel):
    """Emotion analysis result."""

    primary_emotion: EmotionType = Field(
        ..., description="Primary detected emotion"
    )
    emotion_intensity: float = Field(
        ..., ge=0.0, le=1.0, description="Emotion intensity (0.0-1.0)"
    )
    emotion_keywords: list[str] = Field(
        default_factory=list, description="Keywords that indicate the emotion"
    )
    recommended_tone: str = Field(
        ..., description="Recommended response tone based on emotion"
    )
    tone_adjustment: str = Field(
        ..., description="How the response tone was adjusted"
    )


class AutoModeResponse(BaseModel):
    """Response from Auto Mode."""

    answer: str = Field(..., description="Generated response in user's style")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    detected_intent: Optional[str] = Field(
        default=None, description="Detected intent of incoming message"
    )
    suggested_alternatives: list[str] = Field(
        default_factory=list, description="Alternative response suggestions"
    )
    emotion_analysis: Optional[EmotionAnalysis] = Field(
        default=None, description="Emotion analysis of incoming message"
    )
    timing_recommendation: Optional[dict] = Field(
        default=None, description="Recommended response timing"
    )
    context_used: int = Field(
        default=0, description="Number of context messages used"
    )


class ResponseVariation(BaseModel):
    """A single response variation for Assist Mode."""

    style: str = Field(..., description="Style of this variation")
    message: str = Field(..., description="The generated message")
    tone_description: str = Field(
        ..., description="Brief description of the tone used"
    )
    risk_level: str = Field(
        default="low", description="Risk assessment: low/medium/high"
    )


class AssistModeResponse(BaseModel):
    """Response from Assist Mode with multiple variations."""

    situation_analysis: str = Field(
        ..., description="Brief analysis of the situation"
    )
    recommended_approach: str = Field(
        ..., description="Recommended communication approach"
    )
    variations: list[ResponseVariation] = Field(
        ..., description="Generated message variations"
    )
    tips: list[str] = Field(
        default_factory=list, description="Communication tips for this situation"
    )


class GroupMessage(BaseModel):
    """Generated message for a specific group."""

    group_id: str = Field(..., description="Target group ID")
    group_name: str = Field(..., description="Target group name")
    message: str = Field(..., description="Tailored message for this group")
    tone_used: str = Field(..., description="Tone applied to this message")


class AlibiMessageResponse(BaseModel):
    """Response from Alibi Mode for 1:N announcements."""

    original_announcement: str = Field(..., description="Original announcement text")
    group_messages: list[GroupMessage] = Field(
        ..., description="Tailored messages for each group"
    )
    delivery_order_suggestion: list[str] = Field(
        default_factory=list, description="Suggested order of message delivery"
    )


class AlibiImageResponse(BaseModel):
    """Response from Alibi Image generation."""

    image_url: str = Field(..., description="URL of the generated image")
    prompt_used: str = Field(..., description="The prompt sent to DALL-E")
    situation: str = Field(..., description="The depicted situation")
    usage_tips: list[str] = Field(
        default_factory=list, description="Tips for using the image convincingly"
    )
