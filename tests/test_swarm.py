"""Tests for agent-swarm-lite core functionality."""

import asyncio
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_swarm_lite import Agent, Message, MessageBus, Swarm, EventLogger
from agent_swarm_lite.adapters import EchoAdapter, MockAdapter


class TestMessage(unittest.TestCase):
    """Test message creation and serialization."""

    def test_message_creation(self):
        msg = Message(sender="a", recipient="b", content="hello")
        self.assertEqual(msg.sender, "a")
        self.assertEqual(msg.recipient, "b")
        self.assertEqual(msg.content, "hello")
        self.assertIsNotNone(msg.message_id)
        self.assertIsNotNone(msg.timestamp)

    def test_message_to_dict(self):
        msg = Message(sender="a", recipient="b", content="test")
        d = msg.to_dict()
        self.assertIn("message_id", d)
        self.assertEqual(d["sender"], "a")
        self.assertEqual(d["content"], "test")

    def test_message_metadata(self):
        msg = Message(sender="a", recipient="b", content="x", metadata={"key": "val"})
        self.assertEqual(msg.metadata["key"], "val")


class TestMessageBus(unittest.TestCase):
    """Test the message bus."""

    def test_send_and_receive(self):
        bus = MessageBus()
        bus.send(Message(sender="a", recipient="b", content="hello"))
        messages = bus.get_messages_for("b")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "hello")

    def test_broadcast(self):
        bus = MessageBus()
        bus.send(Message(sender="a", recipient="broadcast", content="all"))
        self.assertEqual(len(bus.get_messages_for("b")), 1)
        self.assertEqual(len(bus.get_messages_for("c")), 1)

    def test_count_and_clear(self):
        bus = MessageBus()
        bus.send(Message(sender="a", recipient="b", content="1"))
        bus.send(Message(sender="a", recipient="b", content="2"))
        self.assertEqual(bus.count, 2)
        bus.clear()
        self.assertEqual(bus.count, 0)

    def test_history(self):
        bus = MessageBus()
        bus.send(Message(sender="a", recipient="b", content="first"))
        bus.send(Message(sender="b", recipient="a", content="second"))
        history = bus.get_history()
        self.assertEqual(len(history), 2)


class TestAgent(unittest.TestCase):
    """Test agent creation and execution."""

    def test_agent_creation(self):
        agent = Agent(name="test", instructions="Do things.")
        self.assertEqual(agent.name, "test")
        self.assertEqual(agent.instructions, "Do things.")

    def test_agent_with_tools(self):
        def my_tool(x: int) -> int:
            return x * 2

        agent = Agent(name="test", tools=[my_tool])
        result = agent.call_tool("my_tool", x=5)
        self.assertEqual(result, 10)

    def test_agent_unknown_tool(self):
        agent = Agent(name="test")
        with self.assertRaises(KeyError):
            agent.call_tool("nonexistent")

    def test_echo_adapter_process(self):
        agent = Agent(name="echo", adapter=EchoAdapter())
        result = asyncio.run(agent.process("hello world"))
        self.assertEqual(result, "hello world")

    def test_mock_adapter_process(self):
        agent = Agent(
            name="mock",
            adapter=MockAdapter(responses=["response one", "response two"]),
        )
        r1 = asyncio.run(agent.process("input1"))
        r2 = asyncio.run(agent.process("input2"))
        self.assertEqual(r1, "response one")
        self.assertEqual(r2, "response two")

    def test_agent_repr(self):
        agent = Agent(name="test", model="gpt-4o")
        r = repr(agent)
        self.assertIn("test", r)
        self.assertIn("gpt-4o", r)


class TestSwarm(unittest.TestCase):
    """Test swarm orchestration patterns."""

    def setUp(self):
        self.agent_a = Agent(name="a", adapter=MockAdapter(responses=["output-a"]))
        self.agent_b = Agent(name="b", adapter=MockAdapter(responses=["output-b"]))
        self.agent_c = Agent(name="c", adapter=MockAdapter(responses=["output-c"]))

    def test_pipeline(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b])
        result = swarm.run_pipeline("start", pipeline=["a", "b"])
        self.assertEqual(result, "output-b")

    def test_pipeline_default_order(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b])
        result = swarm.run_pipeline("start")
        self.assertEqual(result, "output-b")

    def test_parallel(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b, self.agent_c])
        results = swarm.run_parallel("input")
        self.assertEqual(results["a"], "output-a")
        self.assertEqual(results["b"], "output-b")
        self.assertEqual(results["c"], "output-c")

    def test_router(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b])
        result = swarm.run_router(
            "test input",
            router_fn=lambda text, names: "b",
        )
        self.assertEqual(result, "output-b")

    def test_get_agent(self):
        swarm = Swarm(agents=[self.agent_a])
        agent = swarm.get_agent("a")
        self.assertEqual(agent.name, "a")

    def test_get_agent_not_found(self):
        swarm = Swarm(agents=[self.agent_a])
        with self.assertRaises(KeyError):
            swarm.get_agent("nonexistent")

    def test_agent_names(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b])
        self.assertEqual(swarm.agent_names, ["a", "b"])

    def test_message_bus_populated(self):
        swarm = Swarm(agents=[self.agent_a, self.agent_b])
        swarm.run_pipeline("start", pipeline=["a", "b"])
        self.assertGreater(swarm.bus.count, 0)


class TestEventLogger(unittest.TestCase):
    """Test event logging."""

    def test_log_and_retrieve(self):
        logger = EventLogger()
        logger.log_event("agent-a", "start", {"key": "val"})
        self.assertEqual(len(logger.events), 1)
        self.assertEqual(logger.events[0].agent_name, "agent-a")

    def test_events_for_agent(self):
        logger = EventLogger()
        logger.log_event("a", "start")
        logger.log_event("b", "start")
        logger.log_event("a", "end")
        self.assertEqual(len(logger.events_for("a")), 2)

    def test_summary(self):
        logger = EventLogger()
        logger.log_event("a", "x")
        logger.log_event("b", "y")
        s = logger.summary()
        self.assertEqual(s["total_events"], 2)
        self.assertIn("a", s["agents"])

    def test_clear(self):
        logger = EventLogger()
        logger.log_event("a", "x")
        logger.clear()
        self.assertEqual(len(logger.events), 0)


if __name__ == "__main__":
    unittest.main()
