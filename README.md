# agent-swarm-lite

A lightweight Python framework for building multi-agent systems. Define specialized agents, wire them together, and let them collaborate on complex tasks -- all in under 50 lines of setup code.

## Why agent-swarm-lite?

Multi-agent orchestration frameworks tend to be massive. **agent-swarm-lite** takes the opposite approach: a small, readable core that gives you the primitives you actually need.

- **Simple agent definition** -- subclass `Agent` or use the functional API
- **Built-in message passing** -- agents communicate through a typed message bus
- **Swarm orchestration** -- run agents in parallel, sequential, or router patterns
- **LLM-agnostic** -- bring any model via a simple adapter interface
- **Async-first** -- built on asyncio for real concurrency
- **Observable** -- built-in event logging for debugging and tracing

## Installation

```bash
pip install agent-swarm-lite
```

Or from source:

```bash
git clone https://github.com/MukundaKatta/agent-swarm-lite.git
cd agent-swarm-lite
pip install -e .
```

## Quick Start

```python
from agent_swarm_lite import Agent, Swarm

# Define agents with simple functions
researcher = Agent(
    name="researcher",
    instructions="You research topics and return key facts.",
    model="gpt-4o",
)

writer = Agent(
    name="writer",
    instructions="You write clear summaries from research notes.",
    model="gpt-4o",
)

# Create a swarm and run a pipeline
swarm = Swarm(agents=[researcher, writer])
result = swarm.run_pipeline(
    input_text="What are the latest trends in quantum computing?",
    pipeline=["researcher", "writer"],
)
print(result)
```

## Architecture

### Agents

An agent is a unit of work with a name, instructions, and optional tools:

```python
agent = Agent(
    name="data-analyst",
    instructions="Analyze CSV data and return insights.",
    tools=[read_csv, compute_stats],
)
```

### Message Bus

Agents communicate through typed messages:

```python
from agent_swarm_lite import Message

msg = Message(
    sender="researcher",
    recipient="writer",
    content="Key finding: quantum error correction improved 10x.",
    metadata={"confidence": 0.95},
)
```

### Swarm Patterns

- **Pipeline** -- agents run sequentially, each receiving the previous output
- **Parallel** -- multiple agents process the same input concurrently
- **Router** -- a routing agent decides which specialist to invoke

## Examples

See the `examples/` directory:

- `examples/pipeline_demo.py` -- sequential multi-agent pipeline
- `examples/parallel_demo.py` -- parallel agent execution
- `examples/router_demo.py` -- dynamic routing between agents

## Project Structure

```
agent-swarm-lite/
  agent_swarm_lite/
    __init__.py        # Public API
    agent.py           # Agent class and functional API
    message.py         # Message types and bus
    swarm.py           # Swarm orchestrator
    adapters.py        # LLM adapter interface
    logger.py          # Event logging and tracing
  examples/
    pipeline_demo.py   # Pipeline pattern demo
    parallel_demo.py   # Parallel pattern demo
    router_demo.py     # Router pattern demo
  tests/
    test_swarm.py      # Core tests
  requirements.txt
  setup.py
  LICENSE
  README.md
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Open an issue or PR.
