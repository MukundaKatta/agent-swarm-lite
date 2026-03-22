"""Swarm orchestrator for multi-agent execution patterns."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from .agent import Agent
from .message import MessageBus
from .logger import EventLogger


class Swarm:
    """Orchestrates multiple agents in various execution patterns.

    Supports pipeline (sequential), parallel, and router patterns
    for multi-agent collaboration.

    Args:
        agents: List of Agent instances.
        logger: Optional event logger for tracing.
    """

    def __init__(
        self,
        agents: list[Agent],
        logger: EventLogger | None = None,
    ):
        self._agents: dict[str, Agent] = {a.name: a for a in agents}
        self.bus = MessageBus()
        self.logger = logger or EventLogger()

    def get_agent(self, name: str) -> Agent:
        """Get an agent by name.

        Raises:
            KeyError: If the agent doesn't exist.
        """
        if name not in self._agents:
            raise KeyError(f"No agent named '{name}'. Available: {list(self._agents.keys())}")
        return self._agents[name]

    @property
    def agent_names(self) -> list[str]:
        """List of all agent names in the swarm."""
        return list(self._agents.keys())

    def run_pipeline(
        self,
        input_text: str,
        pipeline: list[str] | None = None,
    ) -> str:
        """Run agents sequentially in a pipeline.

        Each agent receives the output of the previous agent as input.

        Args:
            input_text: Initial input text.
            pipeline: Ordered list of agent names. Defaults to registration order.

        Returns:
            The final agent's output.
        """
        return asyncio.run(self._run_pipeline_async(input_text, pipeline))

    async def _run_pipeline_async(
        self,
        input_text: str,
        pipeline: list[str] | None = None,
    ) -> str:
        agent_names = pipeline or list(self._agents.keys())
        self.logger.log_event("swarm", "pipeline_start", {
            "agents": agent_names,
            "input_length": len(input_text),
        })

        current_text = input_text
        context: dict[str, Any] = {}

        for name in agent_names:
            agent = self.get_agent(name)
            current_text = await agent.process(
                input_text=current_text,
                context=context,
                bus=self.bus,
                logger=self.logger,
            )
            context[name] = current_text

        self.logger.log_event("swarm", "pipeline_complete", {
            "output_length": len(current_text),
        })
        return current_text

    def run_parallel(self, input_text: str, agent_names: list[str] | None = None) -> dict[str, str]:
        """Run multiple agents in parallel on the same input.

        Args:
            input_text: Input text sent to all agents.
            agent_names: Which agents to run. Defaults to all.

        Returns:
            Dictionary mapping agent names to their outputs.
        """
        return asyncio.run(self._run_parallel_async(input_text, agent_names))

    async def _run_parallel_async(
        self,
        input_text: str,
        agent_names: list[str] | None = None,
    ) -> dict[str, str]:
        names = agent_names or list(self._agents.keys())
        self.logger.log_event("swarm", "parallel_start", {"agents": names})

        tasks = {}
        for name in names:
            agent = self.get_agent(name)
            tasks[name] = agent.process(
                input_text=input_text,
                bus=self.bus,
                logger=self.logger,
            )

        results = await asyncio.gather(*tasks.values())
        output = dict(zip(tasks.keys(), results))

        self.logger.log_event("swarm", "parallel_complete", {
            "agents": names,
        })
        return output

    def run_router(
        self,
        input_text: str,
        router_fn: Callable[[str, list[str]], str],
    ) -> str:
        """Use a routing function to select which agent handles the input.

        Args:
            input_text: The input text.
            router_fn: A function that takes (input_text, agent_names) and returns the chosen agent name.

        Returns:
            The selected agent's output.
        """
        return asyncio.run(self._run_router_async(input_text, router_fn))

    async def _run_router_async(
        self,
        input_text: str,
        router_fn: Callable[[str, list[str]], str],
    ) -> str:
        names = list(self._agents.keys())
        chosen = router_fn(input_text, names)

        self.logger.log_event("swarm", "router_selected", {
            "chosen_agent": chosen,
            "available": names,
        })

        agent = self.get_agent(chosen)
        return await agent.process(
            input_text=input_text,
            bus=self.bus,
            logger=self.logger,
        )
