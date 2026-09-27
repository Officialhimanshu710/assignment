from typing import List, Dict, Any
from src.graph.state import GraphState, TrailerPlan

class DeterministicVerifier:
    """
    Tier 1: Deterministic Engine (Python)
    Fast, zero-LLM checks for asset existence, timecodes, rights, and budgets.
    """
    @staticmethod
    def verify_plan(plan: TrailerPlan, state: GraphState) -> List[Dict[str, Any]]:
        violations = []
        catalog = state.get("candidate_catalog", {})
        constraints = state.get("constraint_matrix", [])
        
        # 1. Macro Trailer Checks
        if plan.duration_seconds > 60:
            violations.append({"type": "DURATION_EXCEEDED", "segment_id": None, "detail": "Trailer exceeds maximum 60s length."})
            
        if plan.total_cost_usd > state.get("budget_limit_usd", 5.0):
            violations.append({"type": "BUDGET_EXCEEDED", "segment_id": None, "detail": "Trailer is over budget."})
            
        # 2. Segment-level Iteration
        for segment in plan.segments:
            # Asset Existence / Hallucination Check
            if segment.clip_id not in catalog:
                violations.append({
                    "type": "MISSING_ASSET", 
                    "segment_id": segment.segment_id, 
                    "detail": f"Unresolved clip_id: {segment.clip_id} not found in index."
                })
                continue
                
            clip = catalog[segment.clip_id]
            
            # Rights Blocklist Evaluation
            for rule in constraints:
                if rule.category == "RIGHTS" and rule.action == "BLOCK":
                    if rule.target_entity.startswith("actor:"):
                        actor_id = rule.target_entity.split(":")[1]
                        if actor_id in clip.primary_character_ids:
                            violations.append({
                                "type": "RIGHTS_VIOLATION",
                                "segment_id": segment.segment_id,
                                "detail": f"Actor {actor_id} is blocked by contract: {rule.source_clause}"
                            })
                    elif rule.target_entity.startswith("track:"):
                        track_id = rule.target_entity.split(":")[1]
                        if track_id == segment.audio_track_id:
                            violations.append({
                                "type": "RIGHTS_VIOLATION",
                                "segment_id": segment.segment_id,
                                "detail": f"Audio track {track_id} is blocked: {rule.source_clause}"
                            })
                            
        return violations

def tier1_deterministic_node(state: GraphState) -> GraphState:
    """Stage 3 - Tier 1 Node"""
    reports = state.get("validation_reports", {})
    plans = state.get("trailer_plans", {})
    
    new_reports = {}
    for audience, plan in plans.items():
        violations = DeterministicVerifier.verify_plan(plan, state)
        # Flush previous reports for this audience and apply current determinist scan
        new_reports[audience] = violations
        
    return {"validation_reports": new_reports}
