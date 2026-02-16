"""
In-Memory Storage for Talk-pleganger

Simple in-memory storage for development and prototyping.
Replace with PostgreSQL for production use.
"""

from typing import Optional
from functools import lru_cache
from ..schemas.persona import PersonaProfile


class MemoryStore:
    """Thread-safe in-memory storage for personas and chat history."""

    def __init__(self):
        self._personas: dict[str, PersonaProfile] = {}
        self._chat_history: dict[str, list[dict]] = {}

    # ============================================================
    # PERSONA OPERATIONS
    # ============================================================
    def get_persona(self, user_id: str) -> Optional[PersonaProfile]:
        """Retrieve a persona by user ID."""
        return self._personas.get(user_id)

    def save_persona(self, persona: PersonaProfile) -> PersonaProfile:
        """Save or update a persona."""
        self._personas[persona.user_id] = persona
        return persona

    def delete_persona(self, user_id: str) -> bool:
        """Delete a persona by user ID."""
        if user_id in self._personas:
            del self._personas[user_id]
            return True
        return False

    def list_personas(self) -> list[PersonaProfile]:
        """List all personas."""
        return list(self._personas.values())

    # ============================================================
    # CHAT HISTORY OPERATIONS
    # ============================================================
    def add_chat_message(
        self, user_id: str, message: dict
    ) -> None:
        """Add a message to chat history."""
        if user_id not in self._chat_history:
            self._chat_history[user_id] = []
        self._chat_history[user_id].append(message)
        # Keep last 100 messages
        self._chat_history[user_id] = self._chat_history[user_id][-100:]

    def get_chat_history(
        self, user_id: str, limit: int = 20
    ) -> list[dict]:
        """Get recent chat history for a user."""
        history = self._chat_history.get(user_id, [])
        return history[-limit:]

    def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history for a user."""
        if user_id in self._chat_history:
            self._chat_history[user_id] = []
            return True
        return False


# Singleton instance
_store_instance: Optional[MemoryStore] = None


@lru_cache()
def get_store() -> MemoryStore:
    """Get the singleton MemoryStore instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance
