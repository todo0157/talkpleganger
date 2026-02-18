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
│   │   ├── auto.py        # Auto 모드 (감정 분석 + 맥락 기억 + 타이밍)
│   │   ├── assist.py      # Assist 모드
│   │   ├── alibi.py       # Alibi 모드
│   │   ├── history.py     # 대화 히스토리
│   │   ├── timing.py      # 답장 타이밍 분석/추천
│   │   ├── followup.py    # 읽씹 대응 메시지
│   │   └── reaction.py    # 리액션 이미지 생성
│   ├── services/          # 비즈니스 로직
│   │   ├── gpt_service.py # GPT API + 후속 메시지 생성
│   │   ├── dalle_service.py # DALL-E + 리액션 이미지
│   │   ├── timing_service.py # 타이밍 분석 서비스
│   │   └── persona_engine.py # 페르소나 분석
│   ├── schemas/           # Pydantic 모델
│   │   ├── timing.py      # 타이밍 스키마
│   │   ├── followup.py    # 읽씹 대응 스키마
│   │   └── reaction_image.py # 리액션 이미지 스키마
│   ├── prompts/           # GPT 프롬프트 템플릿
│   └── storage/           # 저장소
│       ├── database.py    # SQLite DB (+ response_timing 테이블)
│       └── memory_store.py # 인메모리 (deprecated)
├── frontend/              # React 프론트엔드
│   └── src/
│       ├── pages/         # 페이지 컴포넌트
│       │   ├── AutoMode.jsx      # 자동 응답 (맥락+타이밍 포함)
│       │   ├── FollowUpMode.jsx  # 읽씹 대응 페이지
│       │   └── ReactionImagePage.jsx # 이미지 답장 페이지
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
- **다중 인코딩 자동 감지** (UTF-8, UTF-8-BOM, CP949, EUC-KR, UTF-16)
- **모바일/PC 내보내기 형식 모두 지원**
- 상세한 에러 메시지 및 파싱 결과 피드백

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
- **리액션 이미지 생성** (감정 기반)

### 6. TimingService (`app/services/timing_service.py`)
- 카카오톡 대화 패턴에서 응답 시간 분석
- 시간대별 응답 패턴 저장
- 자연스러운 답장 타이밍 추천

## 다중 페르소나 기능

### 카테고리 (PersonaCategory)
| 카테고리 | 아이콘 | 설명 |
|---------|-------|------|
| work | 💼 | 회사/업무용 |
| friend | 👋 | 친구용 |
| family | 🏠 | 가족용 |
| partner | 💕 | 연인용 |
| formal | 🎩 | 격식체/공식 |
| casual | 😎 | 일상/캐주얼 |
| other | 📝 | 기타 |

### 페르소나 필드
- `category`: 페르소나 카테고리
- `description`: 페르소나 설명
- `icon`: 커스텀 이모지 아이콘

### UI 기능
- Auto 모드에서 카테고리별 빠른 페르소나 전환
- 페르소나 목록에 카테고리 배지 표시
- 카테고리 필터로 페르소나 그룹 관리

## 신규 기능 (v2.0)

### 1. Context Memory (대화 맥락 기억)
Auto 모드에서 최근 대화 내용을 자동으로 불러와 더 자연스러운 응답 생성

```python
class AutoModeRequest(BaseModel):
    auto_fetch_context: bool = True     # 자동 맥락 로딩
    context_window_size: int = 10       # 최근 N개 대화 사용 (최대 20)
    include_timing: bool = True         # 타이밍 추천 포함
```

### 2. Timing Recommendation (답장 타이밍 추천)
카카오톡 대화 패턴을 분석하여 자연스러운 답장 시간 추천

| 시간대 | 설명 |
|--------|------|
| early_morning | 6-9시 |
| morning | 9-12시 |
| afternoon | 12-18시 |
| evening | 18-22시 |
| night | 22-6시 |

### 3. Follow-up Messages (읽씹 대응)
답장이 없을 때 자연스러운 후속 메시지 생성

| 전략 | 경과 시간 | 설명 |
|------|----------|------|
| gentle_reminder | 1-2시간 | 부드러운 리마인더 |
| casual_check | 2-4시간 | 가벼운 안부 |
| conversation_starter | 4-8시간 | 새 화제 전환 |
| topic_change | 8-24시간 | 주제 변경 |
| reconnect | 24시간+ | 다시 연결 |

### 4. Reaction Images (이미지 답장)
감정에 맞는 리액션 이미지를 DALL-E로 생성

**지원 감정**: happy, sad, angry, surprised, love, tired, confused, excited, grateful, apologetic

**이미지 스타일**:
- meme: 밈 스타일
- emoji_art: 이모지 아트
- cute_character: 귀여운 캐릭터
- sticker: 스티커
- minimal: 미니멀 라인아트

---

## 신규 기능 (v2.1)

### 1. 향상된 파일 파싱 (Enhanced File Parsing)
카카오톡 내보내기 파일의 인코딩을 자동 감지하고 상세한 에러 피드백을 제공합니다.

**지원 인코딩**: UTF-8, UTF-8-BOM, CP949, EUC-KR, UTF-16, UTF-16-LE, UTF-16-BE

```python
class EncodingDetector:
    ENCODINGS = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'utf-16', 'utf-16-le', 'utf-16-be']

class ParseResult:
    success: bool
    content: str
    encoding_used: str
    error_message: str
```

**개선 사항**:
- 모바일/PC 카카오톡 내보내기 형식 모두 지원
- BOM(Byte Order Mark) 자동 제거
- 라인 엔딩 정규화 (\r\n → \n)
- 감지된 참여자 목록 표시
- 상세한 한국어 에러 메시지

### 2. 수동 편집 모드 (Manual Edit Mode)
Auto 모드에서 생성된 응답을 사용자가 직접 수정할 수 있습니다.

**기능**:
- 자동/수동 모드 전환 토글
- 생성된 답장 직접 편집
- 원본 복원 기능
- 재생성 버튼
- 수정 이력 관리

### 3. 톤 맞춤 공지 (Tone-Based Announcement)
채팅 파일을 분석하여 해당 톡방의 톤에 맞는 공지를 자동 생성합니다.

```python
class ChatToneAnalysis(BaseModel):
    formality_level: str      # formal/semi-formal/casual/intimate
    emoji_usage: str          # none/minimal/moderate/heavy
    common_expressions: list  # 자주 쓰는 표현들
    sentence_endings: list    # 문장 끝맺음 스타일 (~요, ~ㅋㅋ, ~임)
    overall_tone: str         # 전체적인 톤 설명
    recommended_style: str    # 추천 스타일
```

**워크플로우**:
1. 채팅 파일 업로드 → 톤 자동 분석
2. 공지 내용 입력
3. 분석된 톤에 맞춰 공지 자동 생성
4. 대안 버전 제공

### 4. 모바일 설정 바 (Mobile Settings Bar)
모바일에서 고급 설정을 쉽게 접근할 수 있는 하단 고정 바입니다.

**위치**: 하단 네비게이션 바 바로 위에 고정

**기능**:
- 맥락 기억 ON/OFF 토글
- 타이밍 추천 ON/OFF 토글
- 맥락 윈도우 크기 슬라이더

---

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
| `POST /auto/respond` | 자동 응답 생성 (맥락 기억 + 감정 분석 + 타이밍 추천) |
| `POST /assist/suggest` | 멘트 추천 |
| `POST /alibi/announce` | 그룹별 공지 생성 |
| `POST /alibi/analyze-tone` | 채팅 파일 톤 분석 (v2.1) |
| `POST /alibi/announce-with-tone` | 톤 맞춤 공지 생성 (v2.1) |
| `POST /alibi/image` | 알리바이 이미지 생성 |
| `GET /history/{user_id}` | 대화 기록 조회 |
| `GET /history/{user_id}/stats` | 대화 통계 |
| `DELETE /history/{user_id}` | 대화 기록 삭제 |
| `POST /timing/analyze` | 카톡 파일에서 타이밍 패턴 분석 |
| `GET /timing/{persona_id}/recommend` | 답장 타이밍 추천 |
| `GET /timing/{persona_id}/patterns` | 저장된 타이밍 패턴 조회 |
| `POST /followup/suggest` | 읽씹 대응 메시지 생성 |
| `GET /followup/strategies` | 읽씹 대응 전략 목록 |
| `POST /reaction/generate` | 리액션 이미지 생성 |
| `GET /reaction/emotions` | 지원 감정 목록 |
| `GET /reaction/styles` | 이미지 스타일 목록 |

## 데이터 모델

### PersonaProfile
- `user_id`: 사용자 ID
- `name`: 이름
- `category`: 카테고리 (work/friend/family/partner/formal/casual/other)
- `description`: 페르소나 설명
- `icon`: 커스텀 이모지 아이콘
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
- `timing_recommendation`: 답장 타이밍 추천 (신규)
- `context_used`: 사용된 맥락 메시지 수 (신규)

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
3. **response_timing**: 응답 시간 패턴 저장

### 데이터 영속성
- 서버 재시작해도 데이터 유지
- `talkpleganger.db` 파일에 저장

## 주의사항

1. **API 키 보안**: `.env` 파일은 절대 커밋하지 않음
2. **데이터베이스**: `talkpleganger.db` 파일 백업 권장
3. **CORS**: localhost에서만 허용됨
4. **한국어 인코딩**: 카톡 파일은 UTF-8, CP949, EUC-KR 자동 감지

## 테스트 예시

### 직장인 모드 (work)
```
입력: "회의 일정이 변경됐는데 괜찮으시죠?"
응답: "네, 괜찮습니다. 변경된 일정 알려주시면 감사하겠습니다."
신뢰도: 90% | 감정: neutral
```

### 친구 모드 (friend)
```
입력: "야 오늘 PC방 갈래??"
응답: "오 좋아!! 몇 시에 갈까? ㅋㅋㅋ"
신뢰도: 95% | 감정: excited
```

카테고리에 따라 말투가 자동으로 조절됩니다.
