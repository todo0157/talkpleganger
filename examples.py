"""
Talk-pleganger API 사용 예시

이 파일은 API 테스트 및 사용법 예시를 제공합니다.
"""

import httpx

BASE_URL = "http://localhost:8000"


# ============================================================
# 1. 페르소나 생성 예시
# ============================================================
def create_persona_example():
    """사용자 페르소나 생성 예시"""
    payload = {
        "user_id": "user_123",
        "name": "홍길동",
        "chat_examples": [
            {"role": "other", "content": "오늘 저녁 뭐 먹을까?"},
            {"role": "user", "content": "음 치킨 어때요ㅋㅋ 배달시키죠~"},
            {"role": "other", "content": "내일 회의 몇 시야?"},
            {"role": "user", "content": "2시요! 늦지 마세요ㅎㅎ"},
            {"role": "other", "content": "주말에 시간 있어?"},
            {"role": "user", "content": "토요일은 좀 바쁘고 일요일 괜찮아요~"},
            {"role": "other", "content": "고마워!"},
            {"role": "user", "content": "별말씀을요ㅎㅎ 도움이 됐다니 다행이에요"},
        ],
    }

    response = httpx.post(f"{BASE_URL}/persona/", json=payload)
    print("=== 페르소나 생성 ===")
    print(response.json())
    return response.json()


# ============================================================
# 2. Auto Mode 예시
# ============================================================
def auto_mode_example():
    """자동 응답 생성 예시"""
    payload = {
        "user_id": "user_123",
        "incoming_message": {
            "sender_id": "friend_456",
            "sender_name": "김철수",
            "message_text": "이번 주 토요일에 같이 영화 보러 갈래?",
        },
        "response_length": "medium",
    }

    response = httpx.post(f"{BASE_URL}/auto/respond", json=payload)
    print("\n=== Auto Mode 응답 ===")
    print(response.json())
    return response.json()


# ============================================================
# 3. Assist Mode 예시
# ============================================================
def assist_mode_example():
    """멘트 보조 예시 - 상사에게 휴가 요청"""
    payload = {
        "user_id": "user_123",
        "recipient": {
            "name": "김부장",
            "age_group": "50s",
            "relationship": "boss",
            "personality": "업무 중심적이지만 합리적",
            "preferences": "간결하고 명확한 소통 선호",
        },
        "situation": "다음 주 금요일에 개인 사유로 휴가를 쓰고 싶은 상황",
        "goal": "휴가 승인을 받고 싶습니다",
        "variation_styles": ["polite", "logical", "soft"],
    }

    response = httpx.post(f"{BASE_URL}/assist/suggest", json=payload)
    print("\n=== Assist Mode 응답 ===")
    print(response.json())
    return response.json()


# ============================================================
# 4. Alibi Mode - 1:N 공지 예시
# ============================================================
def alibi_announce_example():
    """1:N 공지 생성 예시"""
    payload = {
        "user_id": "user_123",
        "announcement": "이번 주 토요일 저녁에 약속이 생겨서 참석이 어려울 것 같습니다",
        "groups": [
            {
                "group_id": "work",
                "group_name": "직장 동료",
                "tone": "formal",
            },
            {
                "group_id": "friends",
                "group_name": "친구들",
                "tone": "casual",
            },
            {
                "group_id": "family",
                "group_name": "가족",
                "tone": "polite",
            },
        ],
        "context": "갑자기 중요한 개인 일정이 생김",
    }

    response = httpx.post(f"{BASE_URL}/alibi/announce", json=payload)
    print("\n=== Alibi 1:N 공지 ===")
    print(response.json())
    return response.json()


# ============================================================
# 5. Alibi Mode - 이미지 생성 예시
# ============================================================
def alibi_image_example():
    """알리바이 이미지 생성 예시"""
    payload = {
        "user_id": "user_123",
        "situation": "조용한 카페에서 노트북으로 작업 중인 모습",
        "style": "realistic",
        "additional_details": "창가 자리, 아메리카노 한 잔, 자연광",
    }

    response = httpx.post(f"{BASE_URL}/alibi/image", json=payload)
    print("\n=== Alibi 이미지 생성 ===")
    print(response.json())
    return response.json()


# ============================================================
# 전체 테스트 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("톡플갱어 (Talk-pleganger) API 테스트")
    print("=" * 60)

    try:
        # 1. 페르소나 생성
        create_persona_example()

        # 2. Auto Mode
        auto_mode_example()

        # 3. Assist Mode
        assist_mode_example()

        # 4. Alibi 공지
        alibi_announce_example()

        # 5. Alibi 이미지 (DALL-E API 키 필요)
        # alibi_image_example()

        print("\n" + "=" * 60)
        print("테스트 완료!")
        print("=" * 60)

    except httpx.ConnectError:
        print("\n오류: 서버에 연결할 수 없습니다.")
        print("서버를 먼저 실행하세요: uvicorn app.main:app --reload")
