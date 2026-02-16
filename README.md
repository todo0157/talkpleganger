# 톡플갱어 (Talk-pleganger)

> 내 말투를 배우는 AI 카카오톡 비서

카카오톡 대화 스타일을 학습하여 나 대신 답장을 작성해주는 AI 서비스입니다.

## 주요 기능

### 1. Auto Mode (자동 응답) + 감정 분석
- 내 말투 그대로 자동 답장 생성
- **상대방 감정 분석** (기쁨/슬픔/화남/불안 등 10가지)
- **감정에 따른 톤 자동 조절** (화남→차분하게, 슬픔→위로 등)
- 대화 맥락을 이해하고 적절한 응답 제안

### 2. Assist Mode (멘트 추천)
- 상사, 교수님 등 상황별 맞춤 멘트 추천
- 다양한 톤(정중/캐주얼/유머러스)의 변형 제공
- 위험도 표시로 안전한 선택 가능

### 3. Alibi Mode (공지 생성)
- 여러 그룹(가족/친구/직장)에 맞는 공지 동시 생성
- DALL-E를 활용한 알리바이 이미지 생성

### 4. 카카오톡 대화 업로드
- 카카오톡 내보내기 파일(.txt) 직접 업로드
- 1:1 채팅 및 그룹채팅 모두 지원
- 그룹채팅에서 특정 상대만 선택하여 학습 가능

### 5. 대화 히스토리 저장
- SQLite DB로 영구 저장 (서버 재시작해도 유지)
- 대화 기록 조회 및 관리
- 통계 대시보드 (총 대화, 감정 분포, 평균 신뢰도)

## 감정 분석 기능

상대방 메시지의 감정을 자동 분석하고 톤을 조절합니다.

| 감정 | 이모지 | AI 톤 조절 |
|------|--------|-----------|
| 기쁨 (happy) | 😊 | 함께 기뻐하며 긍정적으로 |
| 슬픔 (sad) | 😢 | 공감하며 위로하는 톤 |
| 화남 (angry) | 😠 | 차분하고 이해하는 톤 |
| 불안 (anxious) | 😰 | 안심시키며 지지하는 톤 |
| 흥분 (excited) | 🤩 | 열정적으로 함께 호응 |
| 중립 (neutral) | 😐 | 평소 말투 유지 |
| 혼란 (confused) | 😕 | 명확하고 친절하게 설명 |
| 감사 (grateful) | 🙏 | 겸손하게 받아들이며 |
| 미안함 (apologetic) | 😔 | 관대하게 안심시키며 |
| 긴급 (urgent) | ⚡ | 간결하고 핵심만 |

## 기술 스택

### Backend
- **FastAPI** - Python 웹 프레임워크
- **OpenAI GPT-4o** - AI 응답 생성 + 감정 분석
- **DALL-E 3** - 이미지 생성
- **SQLite** - 데이터 영구 저장
- **Pydantic** - 데이터 검증

### Frontend
- **React 18** - UI 라이브러리
- **Vite** - 빌드 도구
- **React Router** - 라우팅
- **Axios** - HTTP 클라이언트
- **PWA** - 모바일 앱처럼 설치 가능

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/todo0157/talkpleganger.git
cd talkpleganger
```

### 2. Backend 설정
```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 서버 실행
python -m uvicorn app.main:app --port 8002
```

### 3. Frontend 설정
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 4. 접속
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002
- API 문서: http://localhost:8002/docs

## 사용 방법

### 카카오톡 대화 내보내기
1. 카카오톡 대화방 열기
2. 우측 상단 **≡** 메뉴 클릭
3. **대화 내보내기** 선택
4. **텍스트로 저장** 선택

### 페르소나 등록
1. "페르소나 설정" 메뉴로 이동
2. 카카오톡 대화 파일 업로드
3. 대화방에서 사용하는 내 이름 선택
4. (그룹채팅의 경우) 학습할 상대 선택
5. 페르소나 생성 완료

### AI 응답 생성
1. 원하는 모드(Auto/Assist/Alibi) 선택
2. 상황 및 메시지 입력
3. AI가 내 말투로 응답 생성 (+ 감정 분석)
4. 복사하여 카카오톡에 붙여넣기

### 대화 히스토리
1. "히스토리" 메뉴로 이동
2. 이전 대화 기록 확인
3. 통계 (감정 분포, 평균 신뢰도 등) 확인

## 프로젝트 구조

```
talkpleganger/
├── app/                    # Backend
│   ├── main.py            # FastAPI 앱 진입점
│   ├── config.py          # 환경설정
│   ├── routers/           # API 엔드포인트
│   │   ├── persona.py     # 페르소나 관리
│   │   ├── auto.py        # Auto 모드 (감정 분석)
│   │   ├── assist.py      # Assist 모드
│   │   ├── alibi.py       # Alibi 모드
│   │   └── history.py     # 대화 히스토리
│   ├── services/          # 비즈니스 로직
│   │   ├── gpt_service.py # GPT API 연동
│   │   ├── dalle_service.py # DALL-E 연동
│   │   ├── persona_engine.py # 페르소나 분석
│   │   └── kakao_parser.py # 카톡 파싱
│   ├── schemas/           # Pydantic 모델
│   ├── prompts/           # GPT 프롬프트 템플릿
│   └── storage/           # 데이터 저장소
│       └── database.py    # SQLite DB
├── frontend/              # Frontend
│   ├── src/
│   │   ├── App.jsx        # 메인 앱
│   │   ├── api.js         # API 클라이언트
│   │   └── pages/         # 페이지 컴포넌트
│   └── public/            # 정적 파일
├── talkpleganger.db       # SQLite 데이터베이스
├── requirements.txt       # Python 의존성
└── .env.example          # 환경변수 예시
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/persona/` | 페르소나 생성 |
| GET | `/persona/` | 페르소나 목록 |
| POST | `/persona/parse-kakao` | 카톡 파일 파싱 |
| POST | `/persona/create-from-kakao` | 카톡에서 페르소나 생성 |
| POST | `/auto/respond` | Auto 모드 응답 (감정 분석 포함) |
| POST | `/assist/suggest` | Assist 모드 추천 |
| POST | `/alibi/announce` | Alibi 공지 생성 |
| POST | `/alibi/image` | 알리바이 이미지 생성 |
| GET | `/history/{user_id}` | 대화 기록 조회 |
| GET | `/history/{user_id}/stats` | 대화 통계 |
| DELETE | `/history/{user_id}` | 대화 기록 삭제 |

## 스크린샷

### 감정 분석 결과
```
받은 메시지: "야 나 오늘 시험 합격했어!! 너무 기뻐ㅠㅠ"

감정 분석:
- 감정: 😊 기쁨 (happy)
- 강도: 90%
- 키워드: ["합격", "기뻐"]

AI 응답: "우와 정말 축하해요! 저도 너무 기쁘네요!"
```

## 라이선스

MIT License

## 제작

조코딩 해커톤 2025
