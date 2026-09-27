import json
import os
from pydantic import BaseModel
from typing import List, Literal
from src.graph.state import GraphState, TrailerPlan, PlannedSegment
from src.gateway.model_gateway import ModelGateway
from src.catalog.ingest import ingest_node
from src.constraints.compiler import constraint_compiler_node

# --- Schemas for Stage 1.6 Structured Output ---
class ProtectedFact(BaseModel):
    fact_id: str
    description: str
    linked_scene_ids: List[str]
    is_spoiler: bool

class StoryMapOutput(BaseModel):
    core_narrative_facts: List[ProtectedFact]
    relationship_dynamics: List[str]

# --- Schemas for Stage 2 Planner Output ---
class PlannerOutput(BaseModel):
    audience_promise: str
    segments: List[PlannedSegment]

# --- Nodes ---
def story_mapper_node(state: GraphState) -> GraphState:
    raw_manifest = state.get("raw_episode_manifest", {})
    runtime_mode = state.get("runtime_mode", "LIVE")
    budget_limit = state.get("budget_limit_usd", 5.0)
    
    gateway = ModelGateway(mode=runtime_mode, cost_limit=budget_limit)
    prompt = f"Analyze manifest: {json.dumps(raw_manifest)[:2000]}"
    mock_data = {
        "core_narrative_facts": [{"fact_id": "Fact_01", "description": "Detective", "linked_scene_ids": ["scene_04"], "is_spoiler": True}],
        "relationship_dynamics": ["Rivals"]
    }
    
    structured_output = gateway.generate(prompt=prompt, schema=StoryMapOutput, mock_data=mock_data)
    
    os.makedirs("sample_run", exist_ok=True)
    with open("sample_run/story_map.json", "w", encoding="utf-8") as f:
        f.write(structured_output.model_dump_json(indent=2))
        
    return {"protected_facts": [f.model_dump() for f in structured_output.core_narrative_facts]}

def _run_planner(state: GraphState, audience: Literal["family", "young_adult", "dialect_region"], guidelines: str) -> TrailerPlan:
    gateway = ModelGateway(mode=state.get("runtime_mode", "LIVE"), cost_limit=state.get("budget_limit_usd", 5.0))
    catalog_keys = list(state.get("candidate_catalog", {}).keys())
    
    prompt = f"Target: {audience}. Guidelines: {guidelines}. Available IDs: {catalog_keys}."
    mock_data = {
        "audience_promise": f"An engaging experience for {audience}",
        "segments": [{
            "segment_id": f"seg_{audience}_01",
            "clip_id": catalog_keys[0] if catalog_keys else "C001",
            "audio_track_id": "music_01",
            "narrative_function": "Hook",
            "editorial_reasoning": "Strong opening.",
            "cited_evidence": ["scene:01"],
            "risk_flags": []
        }]
    }
    output = gateway.generate(prompt=prompt, schema=PlannerOutput, mock_data=mock_data)
    
    return TrailerPlan(
        trailer_id=f"trailer_{audience}",
        audience=audience,
        duration_seconds=30,
        audience_promise=output.audience_promise,
        segments=output.segments,
        total_cost_usd=0.0,
        validation_status="PENDING"
    )

def planner_family_node(state: GraphState) -> GraphState:
    plan = _run_planner(state, "family", "Filter out violence. Keep it warm.")
    # Safe isolation: copy existing state dictionary and explicitly target subkey
    plans = state.get("trailer_plans", {}).copy()
    plans["family"] = plan
    return {"trailer_plans": plans}

def planner_young_adult_node(state: GraphState) -> GraphState:
    plan = _run_planner(state, "young_adult", "Prioritize pacing. Strictly hide central twist.")
    plans = state.get("trailer_plans", {}).copy()
    plans["young_adult"] = plan
    return {"trailer_plans": plans}

def planner_dialect_node(state: GraphState) -> GraphState:
    plan = _run_planner(state, "dialect_region", "Focus on cultural nuance. Avoid stereotypes.")
    plans = state.get("trailer_plans", {}).copy()
    plans["dialect_region"] = plan
    return {"trailer_plans": plans}

def release_gate_node(state: GraphState) -> GraphState:
    """Stage 5: Release Gate & Timecode Resolver"""
    plans = state.get("trailer_plans", {})
    catalog = state.get("candidate_catalog", {})
    
    for audience, plan in plans.items():
        if plan.validation_status != "FAIL":
            plan.validation_status = "PASS"
            for segment in plan.segments:
                if segment.clip_id in catalog:
                    tc = catalog[segment.clip_id].timecodes
                    segment.source_in = tc.source_in
                    segment.source_out = tc.source_out
                    segment.duration_ms = tc.duration_ms
                    
            output_path = f"sample_run/{audience}_trailer.json"
            os.makedirs("sample_run", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(plan.model_dump_json(indent=2))
                
    return {"trailer_plans": plans}

def escalation_quarantine_node(state: GraphState) -> GraphState:
    """Stage 6: Human Review Escalator"""
    plans = state.get("trailer_plans", {})
    reports = state.get("validation_reports", {})
    
    for audience, plan in plans.items():
        if len(reports.get(audience, [])) > 0:
            plan.validation_status = "FAIL"
            output_path = f"sample_run/{audience}_quarantine.json"
            os.makedirs("sample_run", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(plan.model_dump_json(indent=2))
                
    return {"trailer_plans": plans}

__all__ = [
    "ingest_node", 
    "constraint_compiler_node", 
    "story_mapper_node",
    "planner_family_node",
    "planner_young_adult_node",
    "planner_dialect_node",
    "release_gate_node",
    "escalation_quarantine_node"
]
