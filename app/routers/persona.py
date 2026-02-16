"""
Persona Management Router

Endpoints for creating, updating, and managing user personas.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

from ..schemas.persona import PersonaProfile, PersonaCreate, PersonaUpdate, ChatExample, PersonaCategory
from ..services.persona_engine import PersonaEngine
from ..services.kakao_parser import KakaoParser

router = APIRouter(prefix="/persona", tags=["Persona Management"])


class ParsedChatResponse(BaseModel):
    """Response model for parsed KakaoTalk chat."""
    success: bool
    message: str
    detected_names: list[str]
    chat_examples: list[ChatExample]
    total_messages: int
    is_group_chat: bool = False
    participants: dict[str, int] = {}


class ChatStatsResponse(BaseModel):
    """Response model for chat statistics."""
    total_messages: int
    participant_count: int
    participants: dict[str, int]
    is_group_chat: bool


# ============================================================
# KakaoTalk File Upload Endpoints (MUST be before /{user_id})
# ============================================================

@router.post(
    "/parse-kakao",
    response_model=ParsedChatResponse,
    summary="Parse KakaoTalk exported chat file",
)
async def parse_kakao_chat(
    file: UploadFile = File(...),
    my_name: str = Form(default="나"),
    max_examples: int = Form(default=50),
):
    """
    Parse a KakaoTalk exported chat txt file.

    How to export from KakaoTalk:
    1. Open chat room
    2. Click menu (≡) → Export chat
    3. Select "Save as text"
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported",
        )

    try:
        content = await file.read()

        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode file. Please ensure it's a valid text file.",
            )

        # Get chat statistics
        stats = KakaoParser.get_chat_stats(text)
        detected_names = list(stats["participants"].keys())

        examples = KakaoParser.parse_chat_file(
            content=text,
            my_name=my_name,
            max_examples=max_examples,
        )

        return ParsedChatResponse(
            success=True,
            message=f"Successfully parsed {len(examples)} messages from {stats['participant_count']} participants",
            detected_names=detected_names,
            chat_examples=examples,
            total_messages=len(examples),
            is_group_chat=stats["is_group_chat"],
            participants=stats["participants"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing file: {str(e)}",
        )


@router.post(
    "/create-from-kakao",
    response_model=PersonaProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create persona directly from KakaoTalk file",
)
async def create_persona_from_kakao(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    name: str = Form(...),
    my_name: str = Form(default="나"),
    max_examples: int = Form(default=50),
    category: str = Form(default="other"),
    description: Optional[str] = Form(default=None),
    icon: Optional[str] = Form(default=None),
):
    """Create a persona directly from a KakaoTalk exported chat file."""
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported",
        )

    try:
        content = await file.read()

        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode file.",
            )

        examples = KakaoParser.parse_chat_file(
            content=text,
            my_name=my_name,
            max_examples=max_examples,
        )

        if len(examples) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough messages found. Found {len(examples)}, need at least 3.",
            )

        engine = PersonaEngine()

        existing = engine.get_persona(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Persona for user {user_id} already exists.",
            )

        # Parse category
        try:
            persona_category = PersonaCategory(category)
        except ValueError:
            persona_category = PersonaCategory.OTHER

        persona_data = PersonaCreate(
            user_id=user_id,
            name=name,
            category=persona_category,
            description=description,
            icon=icon,
            chat_examples=examples,
        )

        persona = await engine.create_persona(persona_data)
        return persona

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating persona: {str(e)}",
        )


# ============================================================
# Standard CRUD Endpoints
# ============================================================

@router.get(
    "/",
    response_model=list[PersonaProfile],
    summary="List all personas",
)
async def list_personas():
    """List all registered personas."""
    engine = PersonaEngine()
    return engine.list_personas()


@router.post(
    "/",
    response_model=PersonaProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new persona",
)
async def create_persona(persona_data: PersonaCreate):
    """Create a new persona by analyzing provided chat examples."""
    engine = PersonaEngine()

    existing = engine.get_persona(persona_data.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Persona for user {persona_data.user_id} already exists. Use PUT to update.",
        )

    persona = await engine.create_persona(persona_data)
    return persona


@router.get(
    "/{user_id}",
    response_model=PersonaProfile,
    summary="Get a persona by user ID",
)
async def get_persona(user_id: str):
    """Retrieve a persona profile by user ID."""
    engine = PersonaEngine()
    persona = engine.get_persona(user_id)

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {user_id} not found.",
        )

    return persona


@router.put(
    "/{user_id}",
    response_model=PersonaProfile,
    summary="Update an existing persona",
)
async def update_persona(user_id: str, updates: PersonaUpdate):
    """Update an existing persona with new data."""
    engine = PersonaEngine()

    update_dict = updates.model_dump(exclude_unset=True)
    persona = await engine.update_persona(user_id, update_dict)

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {user_id} not found.",
        )

    return persona


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a persona",
)
async def delete_persona(user_id: str):
    """Delete a persona by user ID."""
    engine = PersonaEngine()
    success = engine.delete_persona(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona for user {user_id} not found.",
        )
