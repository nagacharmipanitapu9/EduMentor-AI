"""
Pluggable LLM backend.

Default: Ollama (https://ollama.com) — fully open-source, runs a local model
(llama3.1, mistral, qwen2.5, ...), no API key, no per-call cost. This is the
right default for a prototype: it proves the agentic pipeline end-to-end on
free/open tooling before anyone commits to a paid provider.

If Ollama isn't installed/running (e.g. this sandbox, a fresh laptop, CI),
we fall back to a deterministic MockLLM so every agent still runs and
produces sensible output. Swap providers with the LLM_PROVIDER env var.
"""

from __future__ import annotations

import os
from typing import Protocol


class LLM(Protocol):
    def invoke(self, prompt: str) -> str: ...


class MockLLM:
    """
    Deterministic, template-based stand-in for a real LLM.

    Doesn't call any network. Used automatically when LLM_PROVIDER=mock or
    when Ollama can't be reached, so `python main.py` always works on a
    bare checkout.
    """

    def invoke(self, prompt: str) -> str:
        # Very small templating: agents pass a `kind` marker as the first
        # line of the prompt so the mock can return something on-topic
        # rather than echoing the whole prompt back.
        first_line = prompt.strip().splitlines()[0] if prompt.strip() else ""
        return f"[mock-llm] {first_line.strip('# ')}"


class OllamaLLM:
    """Thin wrapper around langchain-ollama's ChatOllama."""

    def __init__(self, model: str, base_url: str):
        from langchain_ollama import ChatOllama  # imported lazily

        self._chat = ChatOllama(model=model, base_url=base_url, temperature=0.3)

    def invoke(self, prompt: str) -> str:
        result = self._chat.invoke(prompt)
        return getattr(result, "content", str(result))


def get_llm() -> LLM:
    """
    Build the LLM configured via environment variables, falling back to
    MockLLM on any failure (missing package, Ollama not running, etc.)
    so the graph always runs.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "mock":
        return MockLLM()

    if provider == "ollama":
        try:
            model = os.getenv("OLLAMA_MODEL", "llama3.1")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            llm = OllamaLLM(model=model, base_url=base_url)
            llm.invoke("ping")  # fail fast if Ollama isn't reachable
            return llm
        except Exception:
            print(
                "[llm] Could not reach Ollama at "
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')} "
                "- falling back to MockLLM. Install Ollama and run "
                "`ollama pull llama3.1` to use a real open-source model."
            )
            return MockLLM()

    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")
