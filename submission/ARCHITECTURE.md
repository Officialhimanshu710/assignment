# Autonomous Trailer Director: Architecture Blueprint

## 1. Executive Architectural Blueprint & Design Principles
The Autonomous Trailer Director is architected as an evidence-grounded, constraint-enforcing multi-agent workflow built on LangGraph. It deliberately divorces creative generation from governance logic.

```text
                                      [EPISODE PACKAGE & RULES]
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │  Stage 1: Ingestion   │
                                     │  & Candidate Catalog  │
                                     └───────────┬───────────┘
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │   Stage 2: Semantic   │
                                     │  & Constraint Mapping │
                                     └───────────┬───────────┘
                                                 │
                        ┌────────────────────────┼────────────────────────┐
                        ▼                        ▼                        ▼
              ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
              │  Planner: Family  │    │ Planner: Y. Adult │    │ Planner: Dialect  │
              └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
                        │                        │                        │
                        └────────────────────────┼────────────────────────┘
                                                 │ (Keyed State Merge)
                                                 ▼
                                     ┌───────────────────────┐
                                     │ Stage 4: Verification │
                                     │ Tier 1: Deterministic │
                                     │ Tier 2: Semantic AI   │
                                     └───────────┬───────────┘
                                                 │
                                        [Validation Gate]
                                        /        │        \
                                  (PASS)   (REPAIRABLE)   (UNRESOLVABLE)
                                   /             │             \
                                  v              v              v
                           ┌────────────┐ ┌──────────────┐ ┌──────────────┐
                           │  Release   │ │ Stage 5:     │ │ Stage 6:     │
                           │  Compiler  │ │ Impact & Rep.│ │ Escalation   │
                           └─────┬──────┘ └──────┬───────┘ └──────┬───────┘
                                 │               │                │
                                 v               └───(Loop back)──┘
                           [Final EDL]
```

### Core Design Rules
*   **Deterministic Authority Overrides LLM Discretion**: No LLM evaluates rights, ratings, budget, or scene existence unsupervised. Contracts and policies are compiled into binary constraints executed by standard Python code.
*   **Symbolic Clip References (Zero-Hallucination Timestamps)**: Creative planners output verified symbolic identifiers (`clip_id`), not raw floating-point timestamps. Resolution to exact timecodes (`source_in`, `source_out`) is handled deterministically via an indexed catalog.
*   **State Isolation**: Parallel planner branches execute in isolated memory namespaces keyed by audience to eliminate parallel-write race conditions.
*   **Bounded, Targeted Replanning**: Failures trigger graph localized impact analysis. Only invalidated segments are regenerated; untouched segments and unaffected audience tracks are preserved.

## 2. Graph State & Schema Specifications
The state uses Pydantic models for strict boundary enforcement and TypedDict for the runtime LangGraph state.

## 3. Node-by-Node Pipeline Architecture

```text
                                  [INPUT DATA]
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 1. INGESTION & CATALOG GENERATOR (Deterministic Python)                │
   │    • Parse manifest, subtitles, audio stems, and timecode boundaries.  │
   │    • Index immutable Candidate Clips (C001, C002...) with media refs.  │
   └────────────────────────────────────┬───────────────────────────────────┘
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 1.5 CONSTRAINT COMPILER (Deterministic Python)                         │
   │    • Transform contracts & rating rules into binary ConstraintRules.   │
   │    • Pre-calculate blocklists (restricted actors, expired music).      │
   └────────────────────────────────────┬───────────────────────────────────┘
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 1.6 STORY & SPOILER MAPPER (LLM + Structured Output)                   │
   │    • Extract core narrative facts, relationship dynamics, and twists.  │
   │    • Bind protected plot revelations directly to clip/scene IDs.       │
   └────────────────────────────────────┬───────────────────────────────────┘
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 2. AUDIENCE STRATEGIST & PARALLEL PLANNERS (Isolated LLM Calls)        │
   │    • Generate audience promise and narrative arc (Hook -> Escalation). │
   │    • Select ordered sequences of symbolic `clip_id`s from catalog.     │
   │    • Family: Filter scary scenes; YA: Pace & tension; Dialect: Nuance. │
   └────────────────────────────────────┬───────────────────────────────────┘
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 3. TWO-TIER HYBRID VERIFICATION ENGINE                                 │
   │    Tier 1: Deterministic Engine (Python)                               │
   │      • Asset existence, timecode continuity, rights, duration, budget. │
   │    Tier 2: Semantic Verification (Targeted LLM Evaluators)             │
   │      • Spoiler leakage against protected facts, tone & rating checks.  │
   └────────────────────────────────────┬───────────────────────────────────┘
                                        │
                                 [Adjudicator]
                                 /     │     \
                      All Pass  /      │      \ Failures > Max Retries
                               /    Failures   \
                              v     < Limit     v
   ┌───────────────────────────┐       │       ┌────────────────────────────┐
   │ 5. RELEASE GATE & RESOLVER│       │       │ 6. HUMAN REVIEW ESCALATOR  │
   │    • Map clip_ids to time-│       │       │    • Quarantine trailer.   │
   │      codes deterministical│       │       │    • Emit flagged risks and│
   │    • Export machine-read- │       │       │      actionable questions. │
   │      able EDL JSON.       │       │       └─────────────┬──────────────┘
   └─────────────┬─────────────┘       │                     │
                 │                     v                     │
                 │     ┌───────────────────────────────┐     │
                 │     │ 4. IMPACT ANALYZER & REPLANNER│     │
                 │     │    • Trace violated rule to   │     │
                 │     │      specific segment_id.     │     │
                 │     │    • Query catalog for safe   │     │
                 │     │      alternative clip.        │     │
                 │     │    • Patch plan & loop back.  │     │
                 │     └───────────────┬───────────────┘     │
                 │                     │                     │
                 │                     └──────(Re-verify)────┘
                 ▼                                           ▼
          [Released Trailer]                        [Audited Quarantine]
```

*   **Stage 1: Ingestion & Candidate Clip Catalog (Deterministic)**
    Reads raw episode files, subtitle tracks, and scene manifests to index clips into memory with immutable IDs.
*   **Stage 1.5: Constraint Compiler (Deterministic)**
    Translates legal contracts and platform guidelines into machine-testable records.
*   **Stage 1.6: Story & Spoiler Mapper (LLM)**
    Analyzes narrative progression and maps protected story facts to scene IDs.
*   **Stage 2: Audience Strategy & Parallel Planning (LLM)**
    Runs distinct planning workers concurrently for Family, Young Adult, and Dialect-Region audiences using valid `clip_id`s.
*   **Stage 3: Two-Tier Hybrid Verification Engine**
    
```text
                             Planned Trailer
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ TIER 1: DETERMINISTIC ENGINE (Python - Zero LLM)        │
       ├─────────────────────────────────────────────────────────┤
       │ 1. Timecode Validity: Resolve clip_ids in catalog.      │
       │ 2. Rights Check: Match entities against blocklist.      │
       │ 3. Runtime & Budget: Check target duration & max cost.  │
       └────────────────────────────┬────────────────────────────┘
                                    │
                             (All Rules Pass)
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ TIER 2: SEMANTIC VERIFICATION (Targeted LLMs)           │
       ├─────────────────────────────────────────────────────────┤
       │ 1. Spoiler Exposure: Cross-check against Fact IDs.      │
       │ 2. Rating & Demographics: Scan for unaligned tone.      │
       │ 3. Cultural Respect: Flag dialect misuse/stereotyping.  │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
                          Verification Matrix
```
*   **Stage 4: Impact Analyzer & Selective Replanner**
    Pinpoints failing segments, queries for safe replacements, and patches the plan selectively.
*   **Stage 5: Release Gate & Timecode Resolver**
    Resolves symbolic IDs to exact timecodes and compiles the final JSON EDL.

## 4. Handling Surprise Events & Prompt Injection
*   Untrusted text is isolated.
*   Event simulation capabilities (like sudden rights revocation) trigger targeted replanning.

## 5. Model Gateway & Cost Governance
All inference calls are routed through a `ModelGateway` using Groq. 
*   **Budget Governance**: Halts generation if cost limits are exceeded.
*   **Resilience**: Auto-reroutes on API failure.
*   **Mock Mode**: Supports deterministic replay for testing without API calls.
