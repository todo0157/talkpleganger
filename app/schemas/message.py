from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .persona import RecipientPersona


class MessageMode(str, Enum):
    """Available response generation modes."""

    AUTO = "auto"
    ASSIST = "assist"
    ALIBI = "alibi"


class IncomingMessage(BaseModel):
    """A message received from KakaoTalk."""

    sender_id: str = Field(..., description="Sender's unique identifier")
    sender_name: str = Field(..., description="Sender's display name")
    message_text: str = Field(..., description="The message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")
    chat_room_id: Optional[str] = Field(default=None, description="Chat room identifier")


class AutoModeRequest(BaseModel):
    """Request for Auto Mode - automatic response generation."""

    user_id: str = Field(..., description="User's ID (whose persona to use)")
    incoming_message: IncomingMessage = Field(..., description="The received message")
    context_messages: list[IncomingMessage] = Field(
        default_factory=list, description="Recent conversation context (optional)"
    )
    # Context memory settings
    auto_fetch_context: bool = Field(
        default=True, description="Automatically fetch context from chat history"
    )
    context_window_size: int = Field(
        default=10, ge=1, le=20, description="Number of context messages to fetch"
    )
    # Response preferences
    response_length: Optional[str] = Field(
        default=None, description="Preferred length: short/medium/long"
    )
    include_emoji: Optional[bool] = Field(
        default=None, description="Override emoji usage"
    )
    # Timing recommendation
    include_timing: bool = Field(
        default=True, description="Include timing recommendation in response"
    )


class VariationStyle(str, Enum):
    """Styles for Assist mode variations."""

    POLITE = "polite"
    LOGICAL = "logical"
    SOFT = "soft"
    HUMOROUS = "humorous"


class AssistModeRequest(BaseModel):
    """Request for Assist Mode - guided response suggestions."""

    user_id: str = Field(..., description="User's ID")
    recipient: RecipientPersona = Field(
        ..., description="Information about the recipient"
    )
    situation: str = Field(
        ..., description="Description of the situation/context"
    )
    goal: str = Field(
        ..., description="What the user wants to achieve"
    )
    incoming_message: Optional[IncomingMessage] = Field(
        default=None, description="Optional: message to respond to"
    )
    variation_styles: list[VariationStyle] = Field(
        default=[VariationStyle.POLITE, VariationStyle.LOGICAL, VariationStyle.SOFT],
        description="Which variation styles to generate"
    )


class RecipientGroup(BaseModel):
    """A group of recipients for Alibi mode announcements."""

    group_id: str = Field(..., description="Group identifier")
    group_name: str = Field(..., description="Group name (e.g., 'friends', 'family')")
    tone: str = Field(
        default="casual", description="Tone for this group: formal/casual/intimate"
    )
    recipient_ids: list[str] = Field(
        default_factory=list, description="List of recipient IDs in this group"
    )


class AlibiModeRequest(BaseModel):
    """Request for Alibi Mode - 1:N announcement generation."""

    user_id: str = Field(..., description="User's ID")
    announcement: str = Field(
        ..., description="The core announcement/message to convey"
    )
    groups: list[RecipientGroup] = Field(
        ..., min_length=1, description="Groups to generate messages for"
    )
    context: Optional[str] = Field(
        default=None, description="Additional context or reason"
    )


class AlibiImageRequest(BaseModel):
    """Request for generating an alibi support image via DALL-E."""

    user_id: str = Field(..., description="User's ID")
    situation: str = Field(
        ..., description="The situation to depict (e.g., 'working late at the office')"
    )
    style: str = Field(
        default="realistic", description="Image style: realistic/artistic/minimal"
    )
    additional_details: Optional[str] = Field(
        default=None, description="Extra details to include in the image"
    )


class ChatToneAnalysis(BaseModel):
    """Analysis result of chat tone."""

    formality_level: str = Field(
        ..., description="Formality level: formal/semi-formal/casual/intimate"
    )
    emoji_usage: str = Field(
        ..., description="Emoji usage frequency: none/minimal/moderate/heavy"
    )
    common_expressions: list[str] = Field(
        default_factory=list, description="Common expressions/phrases used"
    )
    sentence_endings: list[str] = Field(
        default_factory=list, description="Common sentence endings (요/임/ㅋㅋ/등)"
    )
    overall_tone: str = Field(
        ..., description="Overall tone description"
    )
    recommended_style: str = Field(
        ..., description="Recommended style for announcements"
    )


class ToneBasedAnnouncementRequest(BaseModel):
    """Request for tone-based announcement generation."""

    user_id: str = Field(..., description="User's ID")
    announcement: str = Field(
        ..., description="The core announcement/message to convey"
    )
    tone_analysis: ChatToneAnalysis = Field(
        ..., description="Analyzed tone from chat"
    )
    group_name: str = Field(
        default="", description="Name of the group/chat room"
    )


class PhotoBasedAlibiRequest(BaseModel):
    """Request for photo-based alibi image generation."""

    situation: str = Field(
        ..., description="The alibi situation to depict (e.g., 'working at a cafe')"
    )
    location: Optional[str] = Field(
        default=None, description="Specific location (e.g., 'Starbucks', 'office')"
    )
    time_of_day: Optional[str] = Field(
        default=None, description="Time of day (morning/afternoon/evening/night)"
    )
    activity: Optional[str] = Field(
        default=None, description="What the person is doing"
    )
    style: str = Field(
        default="realistic", description="Image style: realistic/artistic"
    )


class PhotoAnalysisResult(BaseModel):
    """Result of analyzing an uploaded photo."""

    person_description: str = Field(
        ..., description="Description of the person's appearance"
    )
    clothing_description: str = Field(
        ..., description="Description of clothing/style"
    )
    suggested_scenarios: list[str] = Field(
        default_factory=list, description="Suggested alibi scenarios"
    )
