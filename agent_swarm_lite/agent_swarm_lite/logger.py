"""Event logging and tracing for agent swarms."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Event:
    """A single logged event from an agent or swarm."""

    agent_name: str
    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent_name,
            "type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


class EventLogger:
    """Collects and stores events for debugging and observability.

    Usage:
        logger = EventLogger()
        swarm = Swarm(agents=[...], logger=logger)
        swarm.run_pipeline(...)

        for event in logger.events:
            print(event.to_dict())
    """

    def __init__(self, verbose: bool = False):
        self._events: list[Event] = []
        self.verbose = verbose

    def log_event(
        self,
        agent_name: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Record an event.

        Args:
            agent_name: Name of the agent or component.
            event_type: Type of event (e.g., "process_start").
            data: Optional event data.
        """
        event = Event(
            agent_name=agent_name,
            event_type=event_type,
            data=data or {},
        )
        self._events.append(event)

        if self.verbose:
            ts = event.timestamp.strftime("%H:%M:%S")
            print(f"[{ts}] {agent_name}.{event_type}: {data}")

    @property
    def events(self) -> list[Event]:
        """All recorded events."""
        return list(self._events)

    def events_for(self, agent_name: str) -> list[Event]:
        """Get events for a specific agent."""
        return [e for e in self._events if e.agent_name == agent_name]

    def summary(self) -> dict[str, Any]:
        """Return a summary of all events grouped by agent."""
        agents: dict[str, list[dict]] = {}
        for event in self._events:
            if event.agent_name not in agents:
                agents[event.agent_name] = []
            agents[event.agent_name].append(event.to_dict())
        return {
            "total_events": len(self._events),
            "agents": agents,
        }

    def clear(self) -> None:
        """Clear all recorded events."""
        self._events.clear()
