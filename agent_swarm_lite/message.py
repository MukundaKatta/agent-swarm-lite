"""Typed message passing between agents."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Message:
    """A message passed between agents in a swarm.

    Attributes:
        sender: Name of the sending agent.
        recipient: Name of the receiving agent (or "broadcast").
        content: The message payload (usually text).
        metadata: Optional key-value metadata.
        message_id: Unique identifier (auto-generated).
        timestamp: Creation time (auto-generated).
    """

    sender: str
    recipient: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize the message to a dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class MessageBus:
    """A simple in-memory message bus for agent communication.

    Stores message history and provides mailbox-style retrieval.
    """

    def __init__(self):
        self._history: list[Message] = []

    def send(self, message: Message) -> None:
        """Send a message through the bus."""
        self._history.append(message)

    def get_messages_for(self, agent_name: str) -> list[Message]:
        """Retrieve all messages addressed to a specific agent."""
        return [
            m for m in self._history
            if m.recipient == agent_name or m.recipient == "broadcast"
        ]

    def get_history(self) -> list[Message]:
        """Return the complete message history."""
        return list(self._history)

    def clear(self) -> None:
        """Clear all messages."""
        self._history.clear()

    @property
    def count(self) -> int:
        """Number of messages in the bus."""
        return len(self._history)
