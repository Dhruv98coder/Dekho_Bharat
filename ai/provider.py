import os
from .providers.rule_based import RuleBasedProvider

def get_provider():
    # Upgrade point: set AI_PROVIDER and add a provider class here without
    # changing map, home, or chatbot UI/API contracts.
    name = os.getenv("AI_PROVIDER", "rule_based").lower()
    if name == "rule_based":
        return RuleBasedProvider()
    return RuleBasedProvider()
