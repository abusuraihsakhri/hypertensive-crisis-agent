"""Deterministic mock inference adapter for development and tests.

No external LLM provider is implemented by this repository.
"""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Hypertensive Crisis Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} mock]: Received a local test query. "
            "No language model was called and no clinical assertions were verified."
        )


class LLMFactory:
    """Select the explicitly supported mock provider; fail closed otherwise."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Hypertensive Crisis Agent"):
        prov = str(provider).strip().lower()
        if prov in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError(
            f"Provider {provider!r} is not implemented. "
            "Only the local deterministic mock is supported."
        )
