# CLAUDE.md - 톡플갱어 프로젝트 가이드

이 파일은 AI 어시스턴트가 프로젝트를 이해하고 효과적으로 작업할 수 있도록 돕는 가이드입니다.

## 프로젝트 개요

**톡플갱어 (Talk-pleganger)** - 내 말투를 학습하는 AI 카카오톡 비서

사용자의 카카오톡 대화 스타일을 분석하여 페르소나를 생성하고, 해당 말투로 자동 응답을 생성하는 서비스입니다.

## 기술 스택

### Backend (Python)
- FastAPI 0.100+
- OpenAI API (GPT-4o, DALL-E 3)
- Pydantic v2
- SQLite (영구 저장소)
- Python 3.11+

### Frontend (JavaScript)
- React 18
- Vite
- React Router DOM
- Axios
- PWA (vite-plugin-pwa)

## 프로젝트 구조

```
talkpleganger/
├── app/                    # FastAPI 백엔드
│   ├── main.py            # 앱 진입점, CORS 설정
│   ├── config.py          # 환경변수 설정
│   ├── routers/           # API 라우터
│   │   ├── persona.py     # 페르소나 CRUD
│   │   ├── auto.py        # Auto 모드 (감정 분석 포함)
│   │   ├── assist.py      # Assist 모드
│   │   ├── alibi.py       # Alibi 모드
│   │   └── history.py     # 대화 히스토리
│   ├── services/          # 비즈니스 로직
│   ├── schemas/           # Pydantic 모델
│   ├── prompts/           # GPT 프롬프트 템플릿
│   └── storage/           # 저장소
│       ├── database.py    # SQLite DB
│       └── memory_store.py # 인메모리 (deprecated)
├── frontend/              # React 프론트엔드
│   └── src/
│       ├── pages/         # 페이지 컴포넌트
│       ├── api.js         # API 클라이언트
│       └── App.jsx        # 메인 라우터
└── talkpleganger.db       # SQLite 데이터베이스 파일
```

## 핵심 컴포넌트

### 1. PersonaEngine (`app/services/persona_engine.py`)
- 대화 예시로부터 사용자 말투 분석
- GPT를 사용한 페르소나 특성 추출 (톤, 높임말, 이모지 사용 등)
- SQLite DB에 영구 저장

### 2. KakaoParser (`app/services/kakao_parser.py`)
- 카카오톡 내보내기 파일 파싱
- 1:1 및 그룹채팅 지원
- 참여자 감지 및 메시지 분류

### 3. GPTService (`app/services/gpt_service.py`)
- OpenAI GPT-4o API 연동
- Few-shot 프롬프팅으로 말투 재현
- **감정 분석 및 톤 조절** (10가지 감정 지원)
- JSON 모드로 구조화된 응답 생성

### 4. DatabaseStore (`app/storage/database.py`)
- SQLite 기반 영구 저장소
- 페르소나 및 대화 히스토리 저장
- 대화 통계 및 감정 분포 분석

### 5. DALLEService (`app/services/dalle_service.py`)
- DALL-E 3 이미지 생성
- 알리바이 증거 이미지 생성

## 감정 분석 기능

Auto 모드에서 상대방 메시지의 감정을 분석하고 톤을 자동 조절합니다.

### 지원 감정 (10가지)
| 감정 | 이모지 | 톤 조절 |
|------|--------|---------|
| happy | 😊 | 함께 기뻐하며 긍정적으로 |
| sad | 😢 | 공감하며 위로하는 톤 |
| angry | 😠 | 차분하고 이해하는 톤 |
| anxious | 😰 | 안심시키며 지지하는 톤 |
| excited | 🤩 | 열정적으로 함께 호응 |
| neutral | 😐 | 평소 말투 유지 |
| confused | 😕 | 명확하고 친절하게 설명 |
| grateful | 🙏 | 겸손하게 받아들이며 |
| apologetic | 😔 | 관대하게 안심시키며 |
| urgent | ⚡ | 간결하고 핵심만 |

### EmotionAnalysis 스키마
```python
class EmotionAnalysis(BaseModel):
    primary_emotion: EmotionType  # 주요 감정
    emotion_intensity: float      # 강도 (0.0-1.0)
    emotion_keywords: list[str]   # 감정 키워드
    recommended_tone: str         # 권장 톤
    tone_adjustment: str          # 조절 내용
```

## 서버 실행

### Backend
```bash
cd talkpleganger
python -m uvicorn app.main:app --port 8002
```

### Frontend
```bash
cd talkpleganger/frontend
npm run dev
```

## 환경변수

`.env` 파일에 설정:
```
OPENAI_API_KEY=sk-...
```

## API 포트
- Backend: 8002
- Frontend: 5173

## 주요 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| `POST /persona/` | 페르소나 생성 |
| `POST /persona/parse-kakao` | 카톡 파일 파싱 |
| `POST /persona/create-from-kakao` | 카톡에서 페르소나 생성 |
| `POST /auto/respond` | 자동 응답 생성 (감정 분석 포함) |
| `POST /assist/suggest` | 멘트 추천 |
| `POST /alibi/announce` | 그룹별 공지 생성 |
| `POST /alibi/image` | 알리바이 이미지 생성 |
| `GET /history/{user_id}` | 대화 기록 조회 |
| `GET /history/{user_id}/stats` | 대화 통계 |
| `DELETE /history/{user_id}` | 대화 기록 삭제 |

## 데이터 모델

### PersonaProfile
- `user_id`: 사용자 ID
- `name`: 이름
- `tone`: 말투 (친근/격식/유머러스 등)
- `honorific_level`: 높임말 수준
- `emoji_usage`: 이모지 사용 빈도
- `special_expressions`: 자주 쓰는 표현
- `chat_examples`: 대화 예시

### AutoModeResponse
- `answer`: 생성된 답장
- `confidence_score`: 신뢰도 (0.0-1.0)
- `detected_intent`: 감지된 의도
- `suggested_alternatives`: 대안 답장들
- `emotion_analysis`: 감정 분석 결과

### ChatHistory (DB)
- `id`: 메시지 ID
- `user_id`: 사용자 ID
- `sender_name`: 발신자 이름
- `message_text`: 받은 메시지
- `response_text`: AI 응답
- `emotion`: 감지된 감정
- `emotion_intensity`: 감정 강도
- `confidence_score`: 신뢰도
- `created_at`: 생성 시간

## 데이터베이스

### SQLite 테이블
1. **personas**: 페르소나 프로필 저장
2. **chat_history**: 대화 기록 저장 (감정 분석 포함)

### 데이터 영속성
- 서버 재시작해도 데이터 유지
- `talkpleganger.db` 파일에 저장

## 주의사항

1. **API 키 보안**: `.env` 파일은 절대 커밋하지 않음
2. **데이터베이스**: `talkpleganger.db` 파일 백업 권장
3. **CORS**: localhost에서만 허용됨
4. **한국어 인코딩**: 카톡 파일은 UTF-8, CP949, EUC-KR 자동 감지
