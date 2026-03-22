"""LLM adapter interface and built-in implementations."""

from __future__ import annotations

import abc
from typing import Any


class LLMAdapter(abc.ABC):
    """Abstract base class for LLM adapters.

    Implement this interface to connect any language model
    to agent-swarm-lite. The framework ships with EchoAdapter
    for testing and MockAdapter for demos.
    """

    @abc.abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str = "default",
        tools: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the language model.

        Args:
            prompt: The full prompt text.
            model: Model identifier.
            tools: List of available tool names.
            **kwargs: Additional model parameters.

        Returns:
            The generated text response.
        """
        ...


class EchoAdapter(LLMAdapter):
    """A simple adapter that echoes the input back.

    Useful for testing agent pipelines without calling a real LLM.
    The echo adapter extracts the [Input] section from the prompt
    and returns it, simulating a pass-through agent.
    """

    async def generate(
        self,
        prompt: str,
        model: str = "default",
        tools: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        # Extract the input section
        marker = "[Input] "
        if marker in prompt:
            return prompt.split(marker, 1)[1].strip()
        return prompt


class MockAdapter(LLMAdapter):
    """A mock adapter that returns predefined responses.

    Useful for demos and tests where you want controlled outputs.

    Usage:
        adapter = MockAdapter(responses=["First response", "Second response"])
    """

    def __init__(self, responses: list[str] | None = None):
        self._responses = list(responses or ["Mock response"])
        self._index = 0

    async def generate(
        self,
        prompt: str,
        model: str = "default",
        tools: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        response = self._responses[self._index % len(self._responses)]
        self._index += 1
        return response


class SimpleHTTPAdapter(LLMAdapter):
    """Adapter that calls an OpenAI-compatible HTTP API.

    Works with OpenAI, Anthropic (via proxy), local models
    served by Ollama/vLLM, or any OpenAI-compatible endpoint.

    Usage:
        adapter = SimpleHTTPAdapter(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
    """

    def __init__(
        self,
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        default_model: str = "gpt-4o",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        model: str = "default",
        tools: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for SimpleHTTPAdapter: pip install httpx")

        use_model = model if model != "default" else self.default_model

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": use_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
