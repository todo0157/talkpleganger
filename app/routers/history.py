"""
Chat History Router

Endpoints for managing and viewing chat history.
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from ..storage import get_database

router = APIRouter(prefix="/history", tags=["Chat History"])


class ChatMessage(BaseModel):
    """Chat message model."""
    id: int
    user_id: str
    sender_name: Optional[str]
    sender_id: Optional[str]
    message_text: str
    response_text: Optional[str]
    emotion: Optional[str]
    emotion_intensity: Optional[float]
    confidence_score: Optional[float]
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: list[ChatMessage]
    total_count: int
    has_more: bool


class ChatStatisticsResponse(BaseModel):
    """Response model for chat statistics."""
    total_messages: int
    unique_senders: int
    avg_confidence: float
    first_message: Optional[str]
    last_message: Optional[str]
    emotion_distribution: dict[str, int]


@router.get(
    "/{user_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat history for a user",
)
async def get_chat_history(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Retrieve chat history for a specific user.

    - **user_id**: The user's persona ID
    - **limit**: Maximum number of messages to return (1-100)
    - **offset**: Number of messages to skip (for pagination)
    """
    db = get_database()

    messages = db.get_chat_history(user_id, limit=limit, offset=offset)
    total_count = db.get_chat_history_count(user_id)

    return ChatHistoryResponse(
        messages=[
            ChatMessage(
                id=msg["id"],
                user_id=msg["user_id"],
                sender_name=msg["sender_name"],
                sender_id=msg["sender_id"],
                message_text=msg["message_text"],
                response_text=msg["response_text"],
                emotion=msg["emotion"],
                emotion_intensity=msg["emotion_intensity"],
                confidence_score=msg["confidence_score"],
                created_at=msg["created_at"],
            )
            for msg in messages
        ],
        total_count=total_count,
        has_more=(offset + limit) < total_count,
    )


@router.get(
    "/{user_id}/stats",
    response_model=ChatStatisticsResponse,
    summary="Get chat statistics for a user",
)
async def get_chat_statistics(user_id: str):
    """
    Get statistics about chat history for a user.

    Returns:
    - Total message count
    - Unique senders count
    - Average confidence score
    - First and last message timestamps
    - Emotion distribution
    """
    db = get_database()
    stats = db.get_chat_statistics(user_id)

    return ChatStatisticsResponse(
        total_messages=stats["total_messages"],
        unique_senders=stats["unique_senders"],
        avg_confidence=stats["avg_confidence"],
        first_message=stats["first_message"],
        last_message=stats["last_message"],
        emotion_distribution=stats["emotion_distribution"],
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear chat history for a user",
)
async def clear_chat_history(user_id: str):
    """Clear all chat history for a specific user."""
    db = get_database()
    db.clear_chat_history(user_id)


@router.delete(
    "/message/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific message",
)
async def delete_message(message_id: int):
    """Delete a specific chat message by ID."""
    db = get_database()
    success = db.delete_chat_message(message_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found.",
        )
