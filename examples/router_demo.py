"""Demo: Router pattern for dynamic agent selection.

A routing function examines the input and decides which
specialist agent should handle it.

Run with:
    python examples/router_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_swarm_lite import Agent, Swarm, EventLogger
from agent_swarm_lite.adapters import MockAdapter


def keyword_router(input_text: str, agent_names: list[str]) -> str:
    """Route based on keywords in the input.

    This is a simple demo router. In production, you might
    use an LLM to classify the intent.
    """
    text_lower = input_text.lower()

    if any(kw in text_lower for kw in ["bug", "error", "crash", "fix"]):
        return "debugger"
    elif any(kw in text_lower for kw in ["test", "coverage", "qa"]):
        return "tester"
    elif any(kw in text_lower for kw in ["document", "readme", "explain"]):
        return "documenter"
    else:
        # Default to the first available agent
        return agent_names[0]


def main():
    debugger = Agent(
        name="debugger",
        instructions="Debug code issues and suggest fixes.",
        adapter=MockAdapter(responses=[
            "Bug Analysis: The null pointer exception is caused by an unhandled "
            "edge case in the user validation function. The 'email' field can be "
            "None when OAuth login is used. Fix: add a None check before the "
            "regex validation on line 42."
        ]),
    )

    tester = Agent(
        name="tester",
        instructions="Generate test cases and improve coverage.",
        adapter=MockAdapter(responses=[
            "Test Plan: Added 5 new test cases for the auth module:\n"
            "1. test_oauth_login_no_email - covers the null email case\n"
            "2. test_password_reset_expired_token - edge case for expiry\n"
            "3. test_concurrent_sessions - multi-device login\n"
            "4. test_rate_limit_exceeded - brute force protection\n"
            "5. test_mfa_fallback - SMS when authenticator unavailable"
        ]),
    )

    documenter = Agent(
        name="documenter",
        instructions="Write clear documentation and explanations.",
        adapter=MockAdapter(responses=[
            "Documentation Update: The auth module now supports three login methods:\n"
            "1. Email/password with optional MFA\n"
            "2. OAuth 2.0 (Google, GitHub, Microsoft)\n"
            "3. Magic link (passwordless)\n\n"
            "Each method follows the same session lifecycle: authenticate -> "
            "create session -> set refresh token -> return access token."
        ]),
    )

    logger = EventLogger(verbose=True)
    swarm = Swarm(agents=[debugger, tester, documenter], logger=logger)

    # Test different inputs to show routing behavior
    test_inputs = [
        "There's a bug in the authentication module causing crashes",
        "We need better test coverage for the auth system",
        "Please document how the login flow works",
        "How does the API handle rate limiting?",
    ]

    print("=" * 60)
    print("  Router Demo: Dynamic Agent Selection")
    print("=" * 60)

    for input_text in test_inputs:
        print(f"\n{'- ' * 30}")
        print(f"Input: {input_text}")
        print()

        result = swarm.run_router(
            input_text=input_text,
            router_fn=keyword_router,
        )
        print(f"Output: {result}")

    # Show routing decisions from the log
    print(f"\n{'=' * 60}")
    print("Routing decisions:")
    for event in logger.events:
        if event.event_type == "router_selected":
            print(f"  -> {event.data['chosen_agent']}")


if __name__ == "__main__":
    main()
