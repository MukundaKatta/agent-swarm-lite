"""Agent definition and execution logic."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from .message import Message, MessageBus
from .adapters import LLMAdapter, EchoAdapter
from .logger import EventLogger


class Agent:
    """A single agent in a swarm.

    An agent has a name, a set of instructions, and optionally
    tools (callable functions) and an LLM adapter for generation.

    Args:
        name: Unique agent name.
        instructions: System instructions describing the agent's role.
        model: Model identifier string (used by the adapter).
        tools: List of callable tools the agent can use.
        adapter: LLM adapter for text generation. Defaults to EchoAdapter.
    """

    def __init__(
        self,
        name: str,
        instructions: str = "",
        model: str = "default",
        tools: list[Callable] | None = None,
        adapter: LLMAdapter | None = None,
    ):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = {t.__name__: t for t in (tools or [])}
        self.adapter = adapter or EchoAdapter()

    async def process(
        self,
        input_text: str,
        context: dict[str, Any] | None = None,
        bus: MessageBus | None = None,
        logger: EventLogger | None = None,
    ) -> str:
        """Process an input and return a response.

        Args:
            input_text: The input text to process.
            context: Optional context from previous agents.
            bus: Optional message bus for inter-agent communication.
            logger: Optional event logger for tracing.

        Returns:
            The agent's response text.
        """
        if logger:
            logger.log_event(self.name, "process_start", {"input_length": len(input_text)})

        # Build the prompt with instructions and context
        prompt_parts = []
        if self.instructions:
            prompt_parts.append(f"[Instructions] {self.instructions}")
        if context:
            prompt_parts.append(f"[Context] {context}")
        prompt_parts.append(f"[Input] {input_text}")
        full_prompt = "\n\n".join(prompt_parts)

        # Generate response via adapter
        response = await self.adapter.generate(
            prompt=full_prompt,
            model=self.model,
            tools=list(self.tools.keys()),
        )

        # Post message to bus if available
        if bus:
            msg = Message(
                sender=self.name,
                recipient="broadcast",
                content=response,
                metadata={"model": self.model},
            )
            bus.send(msg)

        if logger:
            logger.log_event(self.name, "process_complete", {"output_length": len(response)})

        return response

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke a registered tool by name.

        Args:
            tool_name: Name of the tool function.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The tool's return value.

        Raises:
            KeyError: If the tool is not registered.
        """
        if tool_name not in self.tools:
            raise KeyError(f"Agent '{self.name}' has no tool '{tool_name}'")
        return self.tools[tool_name](**kwargs)

    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', model='{self.model}', tools={list(self.tools.keys())})"
