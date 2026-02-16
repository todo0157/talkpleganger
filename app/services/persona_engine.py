"""
Persona Learning Engine

Analyzes user chat history to extract linguistic features
and generates persona profiles for accurate mimicking.
"""

import json
from typing import Optional
from openai import AsyncOpenAI

from ..config import get_settings
from ..schemas.persona import PersonaProfile, PersonaCreate, ChatExample, PersonaCategory
from ..prompts import SystemPromptGenerator
from ..storage import get_database


class PersonaEngine:
    """Engine for persona analysis and management."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.store = get_database()

    async def analyze_persona(
        self, chat_examples: list[ChatExample]
    ) -> dict:
        """
        Analyze chat examples to extract linguistic features.

        Returns a dictionary with:
        - sentence_length
        - honorific_level
        - emoji_usage
        - tone
        - special_expressions
        """
        prompt = SystemPromptGenerator.generate_persona_analysis_prompt(
            chat_examples
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 언어학 전문가입니다. 분석 결과를 JSON 형식으로 반환하세요.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)
        return result

    async def create_persona(
        self, persona_data: PersonaCreate
    ) -> PersonaProfile:
        """
        Create a new persona by analyzing chat examples.

        1. Analyze the provided chat examples
        2. Extract linguistic features
        3. Generate system prompt
        4. Save and return the persona
        """
        # Analyze chat examples
        analysis = await self.analyze_persona(persona_data.chat_examples)

        # Create persona profile with analyzed or overridden values
        persona = PersonaProfile(
            user_id=persona_data.user_id,
            name=persona_data.name,
            category=persona_data.category or PersonaCategory.OTHER,
            description=persona_data.description,
            icon=persona_data.icon,
            sentence_length=persona_data.sentence_length or analysis.get("sentence_length", "medium"),
            honorific_level=persona_data.honorific_level or analysis.get("honorific_level", "casual"),
            emoji_usage=persona_data.emoji_usage or analysis.get("emoji_usage", "moderate"),
            tone=persona_data.tone or analysis.get("tone", "friendly"),
            special_expressions=persona_data.special_expressions or analysis.get("special_expressions", []),
            chat_examples=persona_data.chat_examples,
        )

        # Generate and attach system prompt
        persona.system_prompt = SystemPromptGenerator.generate_auto_mode_prompt(
            persona
        )

        # Save to store
        self.store.save_persona(persona)

        return persona

    async def update_persona(
        self, user_id: str, updates: dict
    ) -> Optional[PersonaProfile]:
        """Update an existing persona with new data."""
        existing = self.store.get_persona(user_id)
        if not existing:
            return None

        # Apply updates
        for key, value in updates.items():
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)

        # Regenerate system prompt if chat examples or features changed
        existing.system_prompt = SystemPromptGenerator.generate_auto_mode_prompt(
            existing
        )

        # Save updated persona
        self.store.save_persona(existing)
        return existing

    def get_persona(self, user_id: str) -> Optional[PersonaProfile]:
        """Get a persona by user ID."""
        return self.store.get_persona(user_id)

    def delete_persona(self, user_id: str) -> bool:
        """Delete a persona by user ID."""
        return self.store.delete_persona(user_id)

    def list_personas(self) -> list[PersonaProfile]:
        """List all personas."""
        return self.store.list_personas()
