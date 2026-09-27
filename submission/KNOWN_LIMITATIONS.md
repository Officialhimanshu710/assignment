# Known Limitations & Trade-offs

1. **Mock Gateway Emulation**: Currently, the system uses `MOCK` mode which leverages hardcoded structured outputs for deterministic test stability and cost saving. To connect to Groq, the CLI must be run with `--mode LIVE`.
2. **Audio/Subtitle Slicing**: Stage 1 `CandidateBuilder` uses a simplistic placeholder for timecode parsing and slicing. A production implementation requires real FFMPEG/ffprobe metadata ingestion.
3. **Parallel LLM Invocation**: The Python GIL and LangGraph constraints mean parallel execution of planner nodes could be bottlenecked by network I/O unless asynchronous models are explicitly configured in the underlying `ModelGateway`.
4. **Impact Analyzer Scope**: The replanner currently deterministically selects the "first available" safe clip. A future optimization should implement a vector similarity search to swap the clip with the most semantically equivalent alternative.
