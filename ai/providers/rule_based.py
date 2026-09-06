from .base import AIProvider

class RuleBasedProvider(AIProvider):
    def generate(self, prompt: str, context: dict | None = None) -> str:
        return "I can help with GoPlan places, routes, weather, timing and travel information."
