"""Demo: Sequential pipeline with three agents.

Each agent processes the output of the previous one,
simulating a research-to-summary workflow.

Run with:
    python examples/pipeline_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_swarm_lite import Agent, Swarm, EventLogger
from agent_swarm_lite.adapters import MockAdapter


def main():
    # Create agents with mock responses to simulate a real pipeline
    researcher = Agent(
        name="researcher",
        instructions="Research the given topic and return key facts.",
        adapter=MockAdapter(responses=[
            "Key findings on quantum computing in 2026:\n"
            "1. Error correction reached 99.9% fidelity\n"
            "2. IBM launched a 1000+ qubit processor\n"
            "3. Quantum advantage demonstrated in drug discovery\n"
            "4. Cloud-based quantum access became mainstream"
        ]),
    )

    analyst = Agent(
        name="analyst",
        instructions="Analyze the research and identify the most impactful trends.",
        adapter=MockAdapter(responses=[
            "Analysis: The most impactful trend is the convergence of "
            "quantum error correction advances with practical drug discovery "
            "applications. This represents the first real-world quantum advantage "
            "that affects everyday life. Cloud access democratization ensures "
            "these advances reach a broad developer audience."
        ]),
    )

    writer = Agent(
        name="writer",
        instructions="Write a concise executive summary from the analysis.",
        adapter=MockAdapter(responses=[
            "Executive Summary: Quantum Computing in 2026\n\n"
            "Quantum computing has reached a pivotal milestone. With error "
            "correction now at 99.9% fidelity and practical quantum advantage "
            "demonstrated in drug discovery, the technology has moved from "
            "theoretical promise to tangible impact. Cloud-based quantum "
            "platforms are making these capabilities accessible to developers "
            "worldwide, signaling the beginning of the practical quantum era."
        ]),
    )

    # Set up logging
    logger = EventLogger(verbose=True)

    # Create and run the swarm
    swarm = Swarm(agents=[researcher, analyst, writer], logger=logger)

    print("=" * 60)
    print("  Pipeline Demo: Research -> Analyze -> Write")
    print("=" * 60)
    print()

    result = swarm.run_pipeline(
        input_text="What are the latest breakthroughs in quantum computing?",
        pipeline=["researcher", "analyst", "writer"],
    )

    print("\n" + "-" * 60)
    print("Final output:")
    print("-" * 60)
    print(result)

    # Show event log summary
    print("\n" + "-" * 60)
    print("Event log summary:")
    print("-" * 60)
    summary = logger.summary()
    print(f"Total events: {summary['total_events']}")
    for agent_name, events in summary["agents"].items():
        print(f"  {agent_name}: {len(events)} events")

    # Show message bus history
    print(f"\nMessages on bus: {swarm.bus.count}")
    for msg in swarm.bus.get_history():
        print(f"  [{msg.sender}] -> [{msg.recipient}]: {msg.content[:60]}...")


if __name__ == "__main__":
    main()
