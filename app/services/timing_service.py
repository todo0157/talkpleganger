"""
Response Timing Service

Analyzes and recommends response timing based on user patterns.
"""

import re
from datetime import datetime, timedelta
from typing import Optional

from ..storage.database import get_database
from ..schemas.timing import (
    TimingPattern,
    TimingRecommendation,
    TimingAnalysisRequest,
    TimeOfDay,
    UrgencyLevel,
)


class TimingService:
    """Service for response timing analysis and recommendations."""

    def __init__(self):
        self.db = get_database()

    def get_time_of_day(self, hour: int = None) -> TimeOfDay:
        """Get time of day category for a given hour."""
        if hour is None:
            hour = datetime.now().hour

        if 6 <= hour < 9:
            return TimeOfDay.EARLY_MORNING
        elif 9 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 18:
            return TimeOfDay.AFTERNOON
        elif 18 <= hour < 22:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def analyze_kakao_timing(
        self,
        content: str,
        my_name: str = "나"
    ) -> dict:
        """
        Analyze response timing patterns from KakaoTalk export.

        Returns timing statistics extracted from the chat log.
        """
        # Pattern for KakaoTalk message timestamps
        # Format: 2024년 1월 15일 오후 3:45, 홍길동
        timestamp_pattern = r"(\d{4})년 (\d{1,2})월 (\d{1,2})일 (오전|오후) (\d{1,2}):(\d{2}), (.+)"

        messages = []
        for line in content.split('\n'):
            match = re.match(timestamp_pattern, line)
            if match:
                year, month, day, ampm, hour, minute, sender = match.groups()
                hour = int(hour)
                if ampm == "오후" and hour != 12:
                    hour += 12
                elif ampm == "오전" and hour == 12:
                    hour = 0

                try:
                    dt = datetime(
                        int(year), int(month), int(day),
                        hour, int(minute)
                    )
                    messages.append({
                        "timestamp": dt,
                        "sender": sender.strip(),
                        "is_me": my_name in sender
                    })
                except ValueError:
                    continue

        if len(messages) < 2:
            return {
                "avg_minutes": 5,
                "min_minutes": 1,
                "max_minutes": 30,
                "sample_count": 0,
                "time_of_day_patterns": {}
            }

        # Calculate response times
        response_times = []
        time_of_day_responses = {tod.value: [] for tod in TimeOfDay}

        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]

            # If previous was other person and current is me, calculate response time
            if not prev_msg["is_me"] and curr_msg["is_me"]:
                delta = (curr_msg["timestamp"] - prev_msg["timestamp"]).total_seconds() / 60
                # Filter out unreasonable times (more than 24 hours or negative)
                if 0 < delta < 1440:
                    response_times.append(delta)
                    tod = self.get_time_of_day(prev_msg["timestamp"].hour)
                    time_of_day_responses[tod.value].append(delta)

        if not response_times:
            return {
                "avg_minutes": 5,
                "min_minutes": 1,
                "max_minutes": 30,
                "sample_count": 0,
                "time_of_day_patterns": {}
            }

        # Calculate statistics
        avg_minutes = sum(response_times) / len(response_times)
        min_minutes = min(response_times)
        max_minutes = max(response_times)

        # Calculate time of day patterns
        time_of_day_patterns = {}
        for tod, times in time_of_day_responses.items():
            if times:
                time_of_day_patterns[tod] = sum(times) / len(times)

        return {
            "avg_minutes": round(avg_minutes, 1),
            "min_minutes": round(min_minutes, 1),
            "max_minutes": round(max_minutes, 1),
            "sample_count": len(response_times),
            "time_of_day_patterns": time_of_day_patterns
        }

    def save_timing_pattern(
        self,
        persona_id: str,
        timing_data: dict,
        sender_pattern: str = None
    ) -> TimingPattern:
        """Save analyzed timing pattern to database."""
        self.db.save_timing_pattern(
            persona_id=persona_id,
            avg_minutes=timing_data["avg_minutes"],
            min_minutes=timing_data["min_minutes"],
            max_minutes=timing_data["max_minutes"],
            time_of_day_pref=timing_data.get("time_of_day_patterns", {}),
            sample_count=timing_data.get("sample_count", 0),
            sender_pattern=sender_pattern,
        )

        return TimingPattern(
            persona_id=persona_id,
            avg_response_minutes=timing_data["avg_minutes"],
            min_response_minutes=timing_data["min_minutes"],
            max_response_minutes=timing_data["max_minutes"],
            time_of_day_patterns=timing_data.get("time_of_day_patterns", {}),
            sample_count=timing_data.get("sample_count", 0),
            relationship_type=sender_pattern,
        )

    def get_timing_pattern(
        self,
        persona_id: str,
        sender_pattern: str = None
    ) -> Optional[TimingPattern]:
        """Get stored timing pattern for a persona."""
        data = self.db.get_timing_pattern(persona_id, sender_pattern)
        if not data:
            return None

        return TimingPattern(
            persona_id=persona_id,
            avg_response_minutes=data.get("avg_response_time_minutes", 5),
            min_response_minutes=data.get("min_response_time_minutes", 1),
            max_response_minutes=data.get("max_response_time_minutes", 30),
            time_of_day_patterns=data.get("time_of_day_preference", {}),
            sample_count=data.get("sample_count", 0),
            relationship_type=sender_pattern,
        )

    def recommend_timing(
        self,
        persona_id: str,
        message_emotion: str = None,
        urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
    ) -> TimingRecommendation:
        """
        Recommend appropriate response timing.

        Takes into account:
        - User's historical response patterns
        - Time of day
        - Message urgency
        - Message emotion
        """
        current_hour = datetime.now().hour
        time_of_day = self.get_time_of_day(current_hour)

        # Get stored pattern or use defaults
        pattern = self.get_timing_pattern(persona_id)

        if pattern and pattern.sample_count > 0:
            base_minutes = pattern.avg_response_minutes

            # Adjust based on time of day
            tod_patterns = pattern.time_of_day_patterns
            if time_of_day.value in tod_patterns:
                base_minutes = tod_patterns[time_of_day.value]

            min_range = pattern.min_response_minutes
            max_range = pattern.max_response_minutes
            confidence = min(0.9, 0.5 + (pattern.sample_count * 0.02))
        else:
            # Default values
            base_minutes = 5
            min_range = 1
            max_range = 30
            confidence = 0.5

        # Adjust for urgency
        urgency_multiplier = {
            UrgencyLevel.HIGH: 0.3,
            UrgencyLevel.MEDIUM: 1.0,
            UrgencyLevel.LOW: 1.5,
        }
        base_minutes *= urgency_multiplier.get(urgency, 1.0)

        # Adjust for emotion
        emotion_adjustments = {
            "urgent": 0.2,
            "anxious": 0.5,
            "angry": 0.7,
            "sad": 0.8,
            "excited": 0.6,
            "happy": 1.0,
            "neutral": 1.0,
            "grateful": 1.2,
        }
        if message_emotion:
            base_minutes *= emotion_adjustments.get(message_emotion, 1.0)

        recommended_minutes = max(1, int(base_minutes))

        # Generate reason
        reason_parts = []
        if pattern and pattern.sample_count > 0:
            reason_parts.append(f"평소 응답 패턴 기반 (샘플 {pattern.sample_count}개)")
        else:
            reason_parts.append("기본 추천 (패턴 데이터 없음)")

        if urgency == UrgencyLevel.HIGH:
            reason_parts.append("긴급 메시지로 빠른 응답 권장")
        elif urgency == UrgencyLevel.LOW:
            reason_parts.append("여유로운 메시지로 천천히 응답 가능")

        if message_emotion and message_emotion in ["urgent", "anxious", "angry"]:
            reason_parts.append(f"'{message_emotion}' 감정 감지로 빠른 응답 권장")

        # Generate alternatives
        alternatives = [
            {
                "minutes": max(1, int(min_range)),
                "label": "빠른 응답",
                "description": "급한 경우"
            },
            {
                "minutes": recommended_minutes,
                "label": "권장",
                "description": "자연스러운 타이밍"
            },
            {
                "minutes": int(max_range),
                "label": "여유 있게",
                "description": "바쁜 것처럼 보일 때"
            },
        ]

        natural_range = f"{int(min_range)}-{int(max_range)}분"

        return TimingRecommendation(
            recommended_wait_minutes=recommended_minutes,
            confidence=round(confidence, 2),
            reason=" / ".join(reason_parts),
            time_of_day=time_of_day,
            urgency_level=urgency,
            alternative_timings=alternatives,
            natural_range=natural_range,
        )
