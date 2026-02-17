"""
Reaction Image Router

Endpoints for generating emotion-based reaction images.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas.reaction_image import (
    ReactionImageRequest,
    ReactionImageResponse,
    ReactionEmotion,
    ReactionStyle,
    EmotionInfo,
    StyleInfo,
)
from ..services.dalle_service import DalleService

router = APIRouter(prefix="/reaction", tags=["Reaction Images"])


@router.post(
    "/generate",
    response_model=ReactionImageResponse,
    summary="Generate reaction image",
    description="Generate an emotion-based reaction image using DALL-E.",
)
async def generate_reaction_image(request: ReactionImageRequest):
    """
    Generate an emotion-based reaction image.

    This endpoint creates expressive images suitable for chat reactions:
    - Multiple style options (meme, emoji art, cute character, etc.)
    - Various emotions (happy, sad, angry, surprised, etc.)
    - Optional context for better generation

    Returns the generated image URL with usage suggestions.
    """
    dalle_service = DalleService()
    response = await dalle_service.generate_reaction_image(request)

    return response


@router.get(
    "/emotions",
    summary="List supported emotions",
    description="Get list of supported emotions with emoji representations.",
)
async def list_emotions():
    """
    List all supported emotions for reaction images.

    Each emotion includes:
    - ID for API usage
    - Korean label
    - Representative emoji
    - Related keywords
    """
    emotions = [
        EmotionInfo(
            id="happy",
            label="기쁨",
            emoji="😊",
            keywords=["기쁜", "행복한", "즐거운", "웃음"],
        ),
        EmotionInfo(
            id="sad",
            label="슬픔",
            emoji="😢",
            keywords=["슬픈", "우울한", "눈물"],
        ),
        EmotionInfo(
            id="angry",
            label="화남",
            emoji="😠",
            keywords=["화난", "짜증", "분노"],
        ),
        EmotionInfo(
            id="surprised",
            label="놀람",
            emoji="😲",
            keywords=["놀란", "충격", "깜짝"],
        ),
        EmotionInfo(
            id="love",
            label="사랑",
            emoji="😍",
            keywords=["사랑", "애정", "하트"],
        ),
        EmotionInfo(
            id="tired",
            label="피곤",
            emoji="😴",
            keywords=["피곤한", "지친", "졸린"],
        ),
        EmotionInfo(
            id="confused",
            label="혼란",
            emoji="😕",
            keywords=["혼란", "당황", "이해불가"],
        ),
        EmotionInfo(
            id="excited",
            label="흥분",
            emoji="🤩",
            keywords=["흥분", "신남", "기대"],
        ),
        EmotionInfo(
            id="grateful",
            label="감사",
            emoji="🙏",
            keywords=["감사", "고마움", "감동"],
        ),
        EmotionInfo(
            id="apologetic",
            label="미안함",
            emoji="😔",
            keywords=["미안", "죄송", "사과"],
        ),
    ]

    return {"emotions": [e.model_dump() for e in emotions]}


@router.get(
    "/styles",
    summary="List available styles",
    description="Get list of available image styles.",
)
async def list_styles():
    """
    List all available image styles.

    Each style produces a different visual aesthetic:
    - meme: Internet meme style
    - emoji_art: Large emoji-style art
    - cute_character: Kawaii/chibi character
    - sticker: Messaging app sticker
    - minimal: Minimal line art
    """
    styles = [
        StyleInfo(
            id="meme",
            label="밈 스타일",
            description="재미있는 인터넷 밈 스타일의 이미지",
        ),
        StyleInfo(
            id="emoji_art",
            label="이모지 아트",
            description="크고 표현력 있는 이모지 스타일 일러스트",
        ),
        StyleInfo(
            id="cute_character",
            label="귀여운 캐릭터",
            description="카와이/치비 스타일의 귀여운 캐릭터",
        ),
        StyleInfo(
            id="sticker",
            label="스티커",
            description="카카오톡 이모티콘 같은 스티커 디자인",
        ),
        StyleInfo(
            id="minimal",
            label="미니멀",
            description="심플하고 모던한 라인 아트",
        ),
    ]

    return {"styles": [s.model_dump() for s in styles]}


@router.post(
    "/quick",
    response_model=ReactionImageResponse,
    summary="Quick reaction image",
    description="Generate a quick reaction image with default settings.",
)
async def quick_reaction_image(
    emotion: ReactionEmotion,
    style: ReactionStyle = ReactionStyle.CUTE_CHARACTER,
):
    """
    Generate a quick reaction image with minimal parameters.

    Useful for fast generation without detailed configuration.
    """
    request = ReactionImageRequest(
        user_id="quick",
        emotion=emotion,
        style=style,
    )

    dalle_service = DalleService()
    response = await dalle_service.generate_reaction_image(request)

    return response
