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
│   ├── services/          # 비즈니스 로직
│   ├── schemas/           # Pydantic 모델
│   ├── prompts/           # GPT 프롬프트 템플릿
│   └── storage/           # 인메모리 저장소
└── frontend/              # React 프론트엔드
    └── src/
        ├── pages/         # 페이지 컴포넌트
        ├── api.js         # API 클라이언트
        └── App.jsx        # 메인 라우터
```

## 핵심 컴포넌트

### 1. PersonaEngine (`app/services/persona_engine.py`)
- 대화 예시로부터 사용자 말투 분석
- GPT를 사용한 페르소나 특성 추출 (톤, 높임말, 이모지 사용 등)

### 2. KakaoParser (`app/services/kakao_parser.py`)
- 카카오톡 내보내기 파일 파싱
- 1:1 및 그룹채팅 지원
- 참여자 감지 및 메시지 분류

### 3. GPTService (`app/services/gpt_service.py`)
- OpenAI GPT-4o API 연동
- Few-shot 프롬프팅으로 말투 재현
- JSON 모드로 구조화된 응답 생성

### 4. DALLEService (`app/services/dalle_service.py`)
- DALL-E 3 이미지 생성
- 알리바이 증거 이미지 생성

## 개발 규칙

### 코드 스타일
- Python: PEP 8 준수
- JavaScript: ES6+ 문법 사용
- 한국어 주석 및 문서화 권장

### API 설계
- RESTful 엔드포인트
- Pydantic 모델로 요청/응답 검증
- 에러는 HTTPException으로 처리

### 프론트엔드
- 함수형 컴포넌트 + React Hooks
- CSS 변수로 테마 관리
- 모바일 우선 반응형 디자인

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
| `POST /persona/parse-kakao` | 카톡 파일 파싱 |
| `POST /persona/create-from-kakao` | 카톡에서 페르소나 생성 |
| `POST /auto/respond` | 자동 응답 생성 |
| `POST /assist/suggest` | 멘트 추천 |
| `POST /alibi/announce` | 그룹별 공지 생성 |
| `POST /alibi/image` | 알리바이 이미지 생성 |

## 데이터 모델

### PersonaProfile
- `user_id`: 사용자 ID
- `name`: 이름
- `tone`: 말투 (친근/격식/유머러스 등)
- `honorific_level`: 높임말 수준
- `emoji_usage`: 이모지 사용 빈도
- `signature_expressions`: 자주 쓰는 표현
- `chat_examples`: 대화 예시

### ChatExample
- `role`: "user" | "other"
- `content`: 메시지 내용

## 주의사항

1. **API 키 보안**: `.env` 파일은 절대 커밋하지 않음
2. **인메모리 저장소**: 현재 서버 재시작 시 데이터 초기화됨
3. **CORS**: localhost에서만 허용됨
4. **한국어 인코딩**: 카톡 파일은 UTF-8, CP949, EUC-KR 자동 감지
