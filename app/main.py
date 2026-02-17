"""
Talk-pleganger (톡플갱어) - AI Persona KakaoTalk Assistant

Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import persona_router, auto_router, assist_router, alibi_router
from .routers.history import router as history_router
from .routers.timing import router as timing_router
from .routers.followup import router as followup_router
from .routers.reaction import router as reaction_router

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
## 톡플갱어 (Talk-pleganger) API

사용자의 말투를 학습하여 자동 응답, 멘트 보조, 알리바이 생성을 지원하는 AI 비서 서비스

### 주요 기능

#### 1. Auto Mode (자동 응답)
- 사용자의 말투를 학습하여 자동으로 답장 생성
- Few-shot 프롬프팅으로 개인화된 응답 제공
- 대화 맥락 자동 기억 (Context Memory)
- 답장 타이밍 추천 포함

#### 2. Assist Mode (멘트 보조)
- 상사, 교수 등 어려운 상대에게 보낼 메시지 제안
- 다양한 스타일 변형 (공손, 논리적, 부드러운)
- 상황 분석 및 커뮤니케이션 팁 제공

#### 3. Alibi Mode (알리바이 생성)
- 1:N 공지: 하나의 메시지를 그룹별 톤으로 변환
- 알리바이 이미지: DALL-E 3로 상황 이미지 생성

#### 4. Follow-up Mode (읽씹 대응)
- 답장 없을 때 자연스러운 후속 메시지 생성
- 경과 시간별 전략 추천
- 관계에 맞는 톤 조절

#### 5. Reaction Images (이미지 답장)
- 감정 기반 리액션 이미지 생성
- 다양한 스타일 (밈, 이모지, 캐릭터)
- DALL-E 3 활용

#### 6. Timing Analysis (타이밍 분석)
- 카카오톡 대화 패턴 분석
- 자연스러운 답장 타이밍 추천

### 기술 스택
- Backend: FastAPI + Python
- AI: OpenAI GPT-4o + DALL-E 3
- Storage: SQLite
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(persona_router)
app.include_router(auto_router)
app.include_router(assist_router)
app.include_router(alibi_router)
app.include_router(history_router)
app.include_router(timing_router)
app.include_router(followup_router)
app.include_router(reaction_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": settings.app_name,
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "openai_configured": bool(settings.openai_api_key),
        "model": settings.openai_model,
        "dalle_model": settings.openai_dalle_model,
    }


# ============================================================
# KakaoTalk Mock Webhook (Development)
# ============================================================
@app.post("/kakao/mock-notification", tags=["Development"])
async def mock_kakao_notification(
    sender_name: str,
    message_text: str,
    user_id: str = "default_user",
):
    """
    Mock endpoint for simulating KakaoTalk notifications.

    This is for development and testing purposes.
    In production, this would be replaced by:
    1. Android Notification Listener forwarding
    2. Kakao Business Channel webhook
    """
    from .schemas.message import AutoModeRequest, IncomingMessage
    from .services.persona_engine import PersonaEngine
    from .services.gpt_service import GPTService

    incoming = IncomingMessage(
        sender_id=f"kakao_{sender_name}",
        sender_name=sender_name,
        message_text=message_text,
    )

    request = AutoModeRequest(
        user_id=user_id,
        incoming_message=incoming,
    )

    # Try to generate response
    engine = PersonaEngine()
    persona = engine.get_persona(user_id)

    if not persona:
        return {
            "status": "no_persona",
            "message": f"No persona found for user {user_id}. Create one first via POST /persona/",
        }

    gpt_service = GPTService()
    response = await gpt_service.generate_auto_response(
        persona=persona,
        incoming_message=incoming,
    )

    return {
        "status": "success",
        "incoming": {
            "sender": sender_name,
            "message": message_text,
        },
        "response": response.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
