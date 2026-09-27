# Autonomous Trailer Director

## Overview
The **Autonomous Trailer Director** is a production-grade multi-agent workflow designed to automatically plan, construct, and verify promotional video trailers across distinct audience demographics (e.g., Family, Young Adult, Dialect-Regional). 

It utilizes a robust **LangGraph** architecture that enforces strict deterministic rules (rights, budgets, timecodes) over creative LLM generations (LangChain + Groq), ensuring zero hallucinations and absolute compliance with licensing contracts.

## Key Features
1. **Pydantic State Modeling**: Zero-hallucination data constraints across the graph.
2. **Deterministic Verification (Tier 1)**: Python-native rights and budget enforcement.
3. **Semantic Verification (Tier 2)**: LLM-powered checks for tone, cultural respect, and spoiler leakage.
4. **Targeted Replanning**: Selective patching of violating segments without destroying valid adjacent trailer segments.
5. **Cost Governance**: Real-time LLM token cost estimation and limit capping via a unified `ModelGateway`.

## Execution
This project uses `uv` for lightning-fast dependency management.

### Installation
```bash
uv sync
```

### Running the CLI
Run the pipeline natively across all defined demographics:
```bash
uv run python -m src.cli run --mode MOCK
```
*Note: Ensure `.env` is configured with `Groq_API_Key` and `model` if running in `LIVE` mode.*

## Testing
An automated test suite using `pytest` verifies constraint blocking, prompt injection resilience, and replanning logic.
```bash
uv run python -m pytest tests/
```

## Documentation
Please see the files in the `submission/` directory for deep architectural details:
- `submission/ARCHITECTURE.md`: High-level system design and execution flows.
- `submission/AI_COLLABORATION.md`: Human-AI pair programming approach and insights.
- `submission/KNOWN_LIMITATIONS.md`: Trade-offs and future optimization paths.
