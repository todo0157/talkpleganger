"""
SQLite Database Storage for Talk-pleganger

Provides persistent storage for personas and chat history.
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager
from pathlib import Path

from ..config import get_settings
from ..schemas.persona import PersonaProfile, ChatExample


class DatabaseStore:
    """SQLite-based persistent storage."""

    def __init__(self):
        settings = get_settings()
        self.db_path = Path(settings.database_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database tables."""
        with self._get_cursor() as cursor:
            # Personas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tone TEXT,
                    honorific_level TEXT,
                    emoji_usage TEXT,
                    sentence_length TEXT,
                    special_expressions TEXT,
                    chat_examples TEXT,
                    system_prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    sender_name TEXT,
                    sender_id TEXT,
                    message_text TEXT NOT NULL,
                    response_text TEXT,
                    emotion TEXT,
                    emotion_intensity REAL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES personas(user_id)
                )
            """)

            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_user_id
                ON chat_history(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_created_at
                ON chat_history(created_at)
            """)

    # ============================================================
    # PERSONA OPERATIONS
    # ============================================================
    def get_persona(self, user_id: str) -> Optional[PersonaProfile]:
        """Retrieve a persona by user ID."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM personas WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_persona(row)
            return None

    def save_persona(self, persona: PersonaProfile) -> PersonaProfile:
        """Save or update a persona."""
        with self._get_cursor() as cursor:
            chat_examples_json = json.dumps(
                [{"role": ex.role, "content": ex.content} for ex in persona.chat_examples],
                ensure_ascii=False
            )
            special_expressions_json = json.dumps(
                persona.special_expressions or [],
                ensure_ascii=False
            )

            cursor.execute("""
                INSERT INTO personas (
                    user_id, name, tone, honorific_level, emoji_usage,
                    sentence_length, special_expressions, chat_examples,
                    system_prompt, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    tone = excluded.tone,
                    honorific_level = excluded.honorific_level,
                    emoji_usage = excluded.emoji_usage,
                    sentence_length = excluded.sentence_length,
                    special_expressions = excluded.special_expressions,
                    chat_examples = excluded.chat_examples,
                    system_prompt = excluded.system_prompt,
                    updated_at = excluded.updated_at
            """, (
                persona.user_id,
                persona.name,
                persona.tone,
                persona.honorific_level,
                persona.emoji_usage,
                persona.sentence_length,
                special_expressions_json,
                chat_examples_json,
                persona.system_prompt,
                datetime.now().isoformat()
            ))
        return persona

    def delete_persona(self, user_id: str) -> bool:
        """Delete a persona and its chat history."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM chat_history WHERE user_id = ?",
                (user_id,)
            )
            cursor.execute(
                "DELETE FROM personas WHERE user_id = ?",
                (user_id,)
            )
            return cursor.rowcount > 0

    def list_personas(self) -> list[PersonaProfile]:
        """List all personas."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM personas ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_persona(row) for row in rows]

    def _row_to_persona(self, row: sqlite3.Row) -> PersonaProfile:
        """Convert database row to PersonaProfile."""
        chat_examples_data = json.loads(row["chat_examples"] or "[]")
        chat_examples = [
            ChatExample(role=ex["role"], content=ex["content"])
            for ex in chat_examples_data
        ]
        special_expressions = json.loads(row["special_expressions"] or "[]")

        return PersonaProfile(
            user_id=row["user_id"],
            name=row["name"],
            tone=row["tone"] or "friendly",
            honorific_level=row["honorific_level"] or "casual",
            emoji_usage=row["emoji_usage"] or "moderate",
            sentence_length=row["sentence_length"] or "medium",
            special_expressions=special_expressions,
            chat_examples=chat_examples,
            system_prompt=row["system_prompt"] or "",
        )

    # ============================================================
    # CHAT HISTORY OPERATIONS
    # ============================================================
    def add_chat_message(
        self,
        user_id: str,
        sender_name: str,
        sender_id: str,
        message_text: str,
        response_text: str = None,
        emotion: str = None,
        emotion_intensity: float = None,
        confidence_score: float = None,
    ) -> int:
        """Add a message to chat history. Returns the message ID."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat_history (
                    user_id, sender_name, sender_id, message_text,
                    response_text, emotion, emotion_intensity, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, sender_name, sender_id, message_text,
                response_text, emotion, emotion_intensity, confidence_score
            ))
            return cursor.lastrowid

    def get_chat_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> list[dict]:
        """Get recent chat history for a user."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM chat_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]

    def get_chat_history_count(self, user_id: str) -> int:
        """Get total count of chat history for a user."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row["count"] if row else 0

    def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history for a user."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM chat_history WHERE user_id = ?",
                (user_id,)
            )
            return cursor.rowcount > 0

    def delete_chat_message(self, message_id: int) -> bool:
        """Delete a specific chat message."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM chat_history WHERE id = ?",
                (message_id,)
            )
            return cursor.rowcount > 0

    def get_chat_statistics(self, user_id: str) -> dict:
        """Get chat statistics for a user."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT sender_name) as unique_senders,
                    AVG(confidence_score) as avg_confidence,
                    MIN(created_at) as first_message,
                    MAX(created_at) as last_message
                FROM chat_history
                WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()

            # Get emotion distribution
            cursor.execute("""
                SELECT emotion, COUNT(*) as count
                FROM chat_history
                WHERE user_id = ? AND emotion IS NOT NULL
                GROUP BY emotion
            """, (user_id,))
            emotions = cursor.fetchall()
            emotion_dist = {e["emotion"]: e["count"] for e in emotions}

            return {
                "total_messages": row["total_messages"] or 0,
                "unique_senders": row["unique_senders"] or 0,
                "avg_confidence": round(row["avg_confidence"] or 0, 2),
                "first_message": row["first_message"],
                "last_message": row["last_message"],
                "emotion_distribution": emotion_dist,
            }


# Singleton instance
_db_instance: Optional[DatabaseStore] = None


def get_database() -> DatabaseStore:
    """Get the singleton DatabaseStore instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseStore()
    return _db_instance
