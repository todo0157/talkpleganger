"""
Reaction Image Schemas

Schemas for emotion-based reaction image generation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ReactionStyle(str, Enum):
    """Image style options for reaction images."""
    MEME = "meme"                     # Internet meme style
    EMOJI_ART = "emoji_art"           # Large emoji-style art
    CUTE_CHARACTER = "cute_character" # Kawaii/chibi character
    STICKER = "sticker"               # Messaging app sticker
    MINIMAL = "minimal"               # Minimal line art


class ReactionEmotion(str, Enum):
    """Supported emotions for reaction images."""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    LOVE = "love"
    TIRED = "tired"
    CONFUSED = "confused"
    EXCITED = "excited"
    GRATEFUL = "grateful"
    APOLOGETIC = "apologetic"


class ReactionImageRequest(BaseModel):
    """Request for generating a reaction image."""

    user_id: str = Field(..., description="User's ID")
    emotion: ReactionEmotion = Field(
        ..., description="Target emotion to express"
    )
    message_context: Optional[str] = Field(
        default=None, description="Message context for better image generation"
    )
    style: ReactionStyle = Field(
        default=ReactionStyle.CUTE_CHARACTER,
        description="Image style"
    )
    korean_text: Optional[str] = Field(
        default=None, description="Optional Korean text to include"
    )
    color_preference: Optional[str] = Field(
        default=None, description="Preferred color scheme"
    )


class ReactionImageResponse(BaseModel):
    """Response from reaction image generation."""

    image_url: str = Field(..., description="URL of the generated image")
    emotion: str = Field(..., description="The emotion expressed")
    style: str = Field(..., description="The style used")
    prompt_used: str = Field(..., description="The DALL-E prompt used")
    suggested_usage: str = Field(
        ..., description="When to use this reaction image"
    )
    alternative_prompts: list[str] = Field(
        default_factory=list,
        description="Alternative prompts for regeneration"
    )


class EmotionInfo(BaseModel):
    """Information about a supported emotion."""

    id: str = Field(..., description="Emotion identifier")
    label: str = Field(..., description="Korean label for the emotion")
    emoji: str = Field(..., description="Representative emoji")
    keywords: list[str] = Field(
        default_factory=list, description="Related keywords"
    )


class StyleInfo(BaseModel):
    """Information about a supported style."""

    id: str = Field(..., description="Style identifier")
    label: str = Field(..., description="Korean label for the style")
    description: str = Field(..., description="Style description")
