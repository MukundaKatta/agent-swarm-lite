"""Demo: Parallel agent execution.

Multiple agents process the same input simultaneously,
returning independent results.

Run with:
    python examples/parallel_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_swarm_lite import Agent, Swarm, EventLogger
from agent_swarm_lite.adapters import MockAdapter


def main():
    # Three specialist agents analyze the same topic in parallel
    tech_analyst = Agent(
        name="tech-analyst",
        instructions="Analyze the technical feasibility and innovation.",
        adapter=MockAdapter(responses=[
            "Technical Assessment: The proposed AI-powered code review system "
            "is feasible with current LLM capabilities. Key challenges include "
            "latency (target <2s per review) and accuracy on edge cases. "
            "Recommendation: Start with a focused scope on Python/JS."
        ]),
    )

    market_analyst = Agent(
        name="market-analyst",
        instructions="Analyze market opportunity and competition.",
        adapter=MockAdapter(responses=[
            "Market Assessment: The AI code review market is growing at 35% CAGR. "
            "Key competitors include CodeRabbit, Sourcery, and GitHub Copilot Reviews. "
            "Differentiation opportunity: focus on security-first reviews for "
            "regulated industries (healthcare, finance)."
        ]),
    )

    risk_analyst = Agent(
        name="risk-analyst",
        instructions="Identify risks and mitigation strategies.",
        adapter=MockAdapter(responses=[
            "Risk Assessment: Primary risks include (1) hallucinated suggestions "
            "that introduce bugs, (2) over-reliance reducing developer skills, "
            "(3) IP concerns with code sent to external APIs. "
            "Mitigation: confidence scoring, human-in-the-loop, on-premise option."
        ]),
    )

    logger = EventLogger(verbose=True)
    swarm = Swarm(
        agents=[tech_analyst, market_analyst, risk_analyst],
        logger=logger,
    )

    print("=" * 60)
    print("  Parallel Demo: Multi-perspective Analysis")
    print("=" * 60)
    print()

    results = swarm.run_parallel(
        input_text="Should we build an AI-powered code review tool?",
    )

    print("\n" + "-" * 60)
    print("Results from all agents:")
    print("-" * 60)
    for agent_name, output in results.items():
        print(f"\n[{agent_name}]")
        print(f"  {output}")

    print(f"\nTotal messages on bus: {swarm.bus.count}")


if __name__ == "__main__":
    main()
