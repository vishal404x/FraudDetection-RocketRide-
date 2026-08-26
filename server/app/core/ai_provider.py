from abc import ABC, abstractmethod
from typing import Any, Dict

class AIProvider(ABC):
    @abstractmethod
    def analyze_invoice(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze_email(self, email_payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze_vendor_change(self, change_payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def explain_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        pass


def get_ai_provider() -> AIProvider:
    """Return a default AI provider implementation. In production, this factory will instantiate a RocketRide AI provider if configured; otherwise return a local mock."""
    # Lazy import to avoid heavy deps
    from app.core.ai_mock import MockAIProvider
    return MockAIProvider()
