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
from ..services.kakao_parser import KakaoParser, ParseResult

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
    encoding_used: Optional[str] = None
    error_details: Optional[str] = None
    # Premium feature info
    is_premium_analysis: bool = False
    total_messages_in_file: int = 0
    messages_analyzed: int = 0


class ChatStatsResponse(BaseModel):
    """Response model for chat statistics."""
    total_messages: int
    participant_count: int
    participants: dict[str, int]
    is_group_chat: bool


# ============================================================
# KakaoTalk File Upload Endpoints (MUST be before /{user_id})
# ============================================================

# Free tier limits
FREE_TIER_MAX_EXAMPLES = 50
PREMIUM_MAX_EXAMPLES = 999999  # Virtually unlimited


@router.post(
    "/parse-kakao",
    response_model=ParsedChatResponse,
    summary="Parse KakaoTalk exported chat file",
)
async def parse_kakao_chat(
    file: UploadFile = File(...),
    my_name: str = Form(default="나"),
    max_examples: int = Form(default=50),
    premium_analysis: bool = Form(default=False),
):
    """
    Parse a KakaoTalk exported chat txt file.

    How to export from KakaoTalk:
    1. Open chat room
    2. Click menu (≡) → Export chat
    3. Select "Save as text"

    Supports multiple encodings: UTF-8, CP949, EUC-KR (auto-detected)

    **Premium Feature**: Set `premium_analysis=true` for full message analysis (no limit).
    Free tier is limited to 50 messages.
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="txt 파일만 지원됩니다. 카카오톡에서 '텍스트로 저장'을 선택해주세요.",
        )

    try:
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일이 비어있습니다.",
            )

        # Determine max examples based on premium status
        effective_max = PREMIUM_MAX_EXAMPLES if premium_analysis else min(max_examples, FREE_TIER_MAX_EXAMPLES)

        # Use improved parsing with automatic encoding detection
        examples, parse_result = KakaoParser.parse_from_bytes(
            content=content,
            my_name=my_name,
            max_examples=effective_max,
        )

        if not parse_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parse_result.error_message,
            )

        # Get chat statistics using the decoded content
        stats = KakaoParser.get_chat_stats(parse_result.content)
        detected_names = list(stats["participants"].keys())
        total_messages_in_file = stats["total_messages"]

        if len(examples) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"메시지를 찾을 수 없습니다. '{my_name}'이 대화방에서 사용하는 이름이 맞는지 확인해주세요. 감지된 참여자: {', '.join(detected_names[:5])}",
            )

        # Build message based on premium status
        if premium_analysis:
            message = f"[프리미엄] {stats['participant_count']}명의 참여자로부터 전체 {len(examples)}개 메시지를 분석했습니다 ({parse_result.encoding_used} 인코딩)"
        else:
            if total_messages_in_file > len(examples):
                message = f"{stats['participant_count']}명의 참여자로부터 {len(examples)}개 메시지를 파싱했습니다 (전체 {total_messages_in_file}개 중, 프리미엄으로 전체 분석 가능)"
            else:
                message = f"{stats['participant_count']}명의 참여자로부터 {len(examples)}개 메시지를 파싱했습니다 ({parse_result.encoding_used} 인코딩)"

        return ParsedChatResponse(
            success=True,
            message=message,
            detected_names=detected_names,
            chat_examples=examples,
            total_messages=len(examples),
            is_group_chat=stats["is_group_chat"],
            participants=stats["participants"],
            encoding_used=parse_result.encoding_used,
            is_premium_analysis=premium_analysis,
            total_messages_in_file=total_messages_in_file,
            messages_analyzed=len(examples),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 파싱 중 오류가 발생했습니다: {str(e)}",
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
    premium_analysis: bool = Form(default=False),
):
    """
    Create a persona directly from a KakaoTalk exported chat file.

    Supports multiple encodings: UTF-8, CP949, EUC-KR (auto-detected)

    **Premium Feature**: Set `premium_analysis=true` for full message analysis.
    Free tier is limited to 50 messages for persona creation.
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="txt 파일만 지원됩니다. 카카오톡에서 '텍스트로 저장'을 선택해주세요.",
        )

    try:
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일이 비어있습니다.",
            )

        # Determine max examples based on premium status
        effective_max = PREMIUM_MAX_EXAMPLES if premium_analysis else min(max_examples, FREE_TIER_MAX_EXAMPLES)

        # Use improved parsing with automatic encoding detection
        examples, parse_result = KakaoParser.parse_from_bytes(
            content=content,
            my_name=my_name,
            max_examples=effective_max,
        )

        if not parse_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parse_result.error_message,
            )

        if len(examples) < 3:
            # Get detected names for helpful error message
            stats, _ = KakaoParser.get_stats_from_bytes(content)
            detected_names = list(stats.get("participants", {}).keys())[:5]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"충분한 메시지를 찾을 수 없습니다 ({len(examples)}개 발견, 최소 3개 필요). "
                       f"'{my_name}'이 대화방에서 사용하는 이름이 맞는지 확인해주세요. "
                       f"감지된 참여자: {', '.join(detected_names) if detected_names else '없음'}",
            )

        engine = PersonaEngine()

        existing = engine.get_persona(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{user_id}' ID의 페르소나가 이미 존재합니다. 다른 ID를 사용하거나 기존 페르소나를 삭제해주세요.",
            )

        # Parse category
        try:
            persona_category = PersonaCategory(category)
        except ValueError:
            persona_category = PersonaCategory.OTHER

        # Add premium indicator to description if premium analysis was used
        final_description = description
        if premium_analysis:
            premium_note = f"[프리미엄 분석: {len(examples)}개 메시지]"
            final_description = f"{premium_note} {description}" if description else premium_note

        persona_data = PersonaCreate(
            user_id=user_id,
            name=name,
            category=persona_category,
            description=final_description,
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
            detail=f"페르소나 생성 중 오류가 발생했습니다: {str(e)}",
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
