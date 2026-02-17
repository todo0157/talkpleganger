"""
Follow-up Message Schemas

Schemas for generating follow-up messages when there's no response.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FollowUpStrategy(str, Enum):
    """Follow-up message strategies based on elapsed time."""
    GENTLE_REMINDER = "gentle_reminder"       # 1-2 hours
    CASUAL_CHECK = "casual_check"             # 2-4 hours
    CONVERSATION_STARTER = "conversation_starter"  # 4-8 hours
    TOPIC_CHANGE = "topic_change"             # 8-24 hours
    RECONNECT = "reconnect"                   # 24+ hours


class TonePreference(str, Enum):
    """Tone preferences for follow-up messages."""
    CASUAL = "casual"
    FORMAL = "formal"
    PLAYFUL = "playful"
    CONCERNED = "concerned"


class FollowUpRequest(BaseModel):
    """Request for follow-up message generation."""

    user_id: str = Field(..., description="User's persona ID")
    last_message_text: str = Field(
        ..., description="The last message that was sent"
    )
    last_message_time: Optional[str] = Field(
        default=None, description="When the last message was sent"
    )
    hours_elapsed: float = Field(
        ..., ge=0, description="Hours since last message"
    )
    recipient_relationship: str = Field(
        ..., description="Relationship with the recipient (boss, friend, etc.)"
    )
    original_intent: Optional[str] = Field(
        default=None, description="Original intent of the conversation"
    )
    tone_preference: Optional[TonePreference] = Field(
        default=None, description="Preferred tone for follow-up"
    )


class FollowUpSuggestion(BaseModel):
    """A single follow-up message suggestion."""

    message: str = Field(..., description="The follow-up message")
    strategy: FollowUpStrategy = Field(
        ..., description="Strategy used for this suggestion"
    )
    tone_description: str = Field(
        ..., description="Description of the tone used"
    )
    risk_level: str = Field(
        default="low", description="Risk level: low/medium/high"
    )
    recommended_for: str = Field(
        ..., description="When to use this message"
    )


class FollowUpResponse(BaseModel):
    """Response containing follow-up message suggestions."""

    elapsed_hours: float = Field(..., description="Hours elapsed")
    recommended_strategy: FollowUpStrategy = Field(
        ..., description="Recommended strategy based on time"
    )
    strategy_explanation: str = Field(
        ..., description="Why this strategy is recommended"
    )
    suggestions: list[FollowUpSuggestion] = Field(
        ..., description="List of follow-up suggestions"
    )
    tips: list[str] = Field(
        default_factory=list, description="Tips for follow-up messaging"
    )
    should_wait_more: bool = Field(
        default=False, description="Whether to wait longer before messaging"
    )
    recommended_additional_wait_hours: Optional[float] = Field(
        default=None, description="Additional hours to wait if should_wait_more is True"
    )
