# AI Collaboration Report

## Approach
This project was developed through active pair-programming with an AI Coding Agent. The architectural blueprint was drafted by the human engineer, establishing strict design principles such as deterministic overriding of LLMs and keyed state isolation. 

The AI agent then incrementally scaffolded the project:
1. **Pydantic State Modeling**: Ensured zero-hallucination data constraints.
2. **Deterministic Pipelines**: Engineered the constraint compiler and tier-1 validation logic to block hallucinations or rights issues.
3. **LLM Planners**: Integrated the LangGraph parallel nodes utilizing Groq and LangChain.
4. **Adjudication & Repair**: Built a robust looping system to patch uncompliant trailers selectively.

## Division of Labor
- **Human (Junior AI Native Engineer)**: System design, architecture planning, LLM environment configuration (API Keys/Model selection), review of concurrent state mutation bugs.
- **AI Agent**: Code scaffolding, deterministic validation logic implementation, LangGraph workflow assembly, CLI creation, and dynamic bug fixing.

## Key Learnings
- **LangGraph Concurrency**: Encountered `InvalidUpdateError` due to parallel branches writing to the same state dictionary. Resolved by employing `typing.Annotated` with a custom `merge_dicts` Python reducer, allowing isolated dictionary mutations safely.
- **Deterministic AI Constraints**: Learned how to effectively "box in" creative LLMs by gating them behind standard deterministic Python logic for rights and budget checks, completely mitigating prompt-injection risks.
- **Environment Management**: Connected the `ModelGateway` to dynamically read model versions and API keys via `.env` injection.
