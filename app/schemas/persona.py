from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ChatExample(BaseModel):
    """A single chat message example for persona learning."""

    role: str = Field(
        ..., description="'user' for user's message, 'other' for the other person"
    )
    content: str = Field(..., description="The message content")


class PersonaProfile(BaseModel):
    """User's linguistic persona profile extracted from chat history."""

    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's display name")

    # Linguistic features
    sentence_length: str = Field(
        default="medium", description="Typical sentence length: short/medium/long"
    )
    honorific_level: str = Field(
        default="casual", description="Honorific usage: formal/polite/casual/intimate"
    )
    emoji_usage: str = Field(
        default="moderate", description="Emoji frequency: none/rare/moderate/frequent"
    )
    tone: str = Field(
        default="friendly", description="Overall tone: formal/friendly/playful/serious"
    )
    special_expressions: list[str] = Field(
        default_factory=list, description="Unique phrases or expressions the user often uses"
    )

    # Chat examples for few-shot learning
    chat_examples: list[ChatExample] = Field(
        default_factory=list, description="Sample conversations for persona mimicking"
    )

    # Generated system prompt
    system_prompt: Optional[str] = Field(
        default=None, description="Auto-generated system prompt for GPT"
    )


class PersonaCreate(BaseModel):
    """Request model for creating a new persona."""

    user_id: str
    name: str
    chat_examples: list[ChatExample] = Field(
        ..., min_length=3, description="At least 3 chat examples required"
    )
    # Optional manual overrides
    sentence_length: Optional[str] = None
    honorific_level: Optional[str] = None
    emoji_usage: Optional[str] = None
    tone: Optional[str] = None
    special_expressions: Optional[list[str]] = None


class PersonaUpdate(BaseModel):
    """Request model for updating an existing persona."""

    name: Optional[str] = None
    chat_examples: Optional[list[ChatExample]] = None
    sentence_length: Optional[str] = None
    honorific_level: Optional[str] = None
    emoji_usage: Optional[str] = None
    tone: Optional[str] = None
    special_expressions: Optional[list[str]] = None


class RelationshipType(str, Enum):
    """Types of relationships with the message recipient."""

    BOSS = "boss"
    COLLEAGUE = "colleague"
    CLIENT = "client"
    PROFESSOR = "professor"
    PARENT = "parent"
    FRIEND = "friend"
    PARTNER = "partner"
    ACQUAINTANCE = "acquaintance"


class RecipientPersona(BaseModel):
    """Persona information about the message recipient."""

    name: Optional[str] = Field(default=None, description="Recipient's name")
    age_group: Optional[str] = Field(
        default=None, description="Age group: 20s/30s/40s/50s/60s+"
    )
    gender: Optional[str] = Field(default=None, description="Gender if relevant")
    relationship: RelationshipType = Field(
        ..., description="Relationship with the user"
    )
    personality: Optional[str] = Field(
        default=None, description="Brief personality description"
    )
    preferences: Optional[str] = Field(
        default=None, description="Communication preferences"
    )
