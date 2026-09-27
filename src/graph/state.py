from typing import TypedDict, Literal, Optional, List, Dict, Annotated
from pydantic import BaseModel, Field

def merge_dicts(a: Dict, b: Dict) -> Dict:
    if not isinstance(a, dict):
        return b.copy() if isinstance(b, dict) else {}
    if not isinstance(b, dict):
        return a.copy()
    merged = a.copy()
    merged.update(b)
    return merged

class TimecodeSpan(BaseModel):
    source_in: str   # Format: "HH:MM:SS.mmm"
    source_out: str  # Format: "HH:MM:SS.mmm"
    duration_ms: int

class CandidateClip(BaseModel):
    clip_id: str
    scene_id: str
    timecodes: TimecodeSpan
    primary_character_ids: List[str]
    dialogue_ids: List[str]
    audio_track_ids: List[str]
    intensity_score: float = Field(ge=0.0, le=1.0)
    cultural_context_tags: List[str]
    has_spoilers: bool = False

class ConstraintRule(BaseModel):
    rule_id: str
    category: Literal["RIGHTS", "RATING", "SPOILER", "BUDGET", "CULTURAL"]
    target_entity: str            # e.g., "actor:actor_04", "track:music_03"
    condition: str                # Deterministic check condition
    action: Literal["BLOCK", "WARN"]
    source_clause: str            # Traceability to policy/contract text

class PlannedSegment(BaseModel):
    segment_id: str
    clip_id: str                  # Resolves against CandidateClip catalog
    source_in: Optional[str] = None
    source_out: Optional[str] = None
    duration_ms: Optional[int] = None
    audio_track_id: str
    subtitle_track_id: Optional[str] = None
    narrative_function: str       # "Hook", "Escalation", "Climax", "Callout"
    editorial_reasoning: str
    cited_evidence: List[str]     # ["scene:07", "contract:music_03"]
    risk_flags: List[str] = []

class TrailerPlan(BaseModel):
    trailer_id: str
    audience: Literal["family", "young_adult", "dialect_region"]
    duration_seconds: int
    audience_promise: str
    segments: List[PlannedSegment]
    total_cost_usd: float
    validation_status: Literal["PENDING", "PASS", "PASS_WITH_WARNINGS", "FAIL"]

class GraphState(TypedDict):
    # Ingested & Compiled Truth Stores
    raw_episode_manifest: dict
    candidate_catalog: Dict[str, CandidateClip]
    constraint_matrix: List[ConstraintRule]
    protected_facts: List[dict]
    
    # Execution Tracking Keyed Per Audience (Safe parallel writes via reducer)
    trailer_plans: Annotated[Dict[str, TrailerPlan], merge_dicts]
    validation_reports: Annotated[Dict[str, List[dict]], merge_dicts]
    repair_attempts: Annotated[Dict[str, int], merge_dicts]
    
    # Financial & Run Telemetry
    accumulated_cost_usd: float
    budget_limit_usd: float
    runtime_mode: Literal["LIVE", "REPLAY", "FALLBACK"]
