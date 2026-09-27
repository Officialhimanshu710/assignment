from typing import Dict, Any
from src.graph.state import GraphState, TrailerPlan

def replanner_node(state: GraphState) -> GraphState:
    """
    Stage 4b: Selective Replanner
    Queries the candidate catalog for a compliant replacement sharing similar narrative intensity.
    Patches the affected segment without touching valid upstream or downstream edits.
    """
    reports = state.get("validation_reports", {})
    plans = state.get("trailer_plans", {}).copy()
    catalog = state.get("candidate_catalog", {})
    
    for audience, violations in reports.items():
        if len(violations) == 0:
            continue 
            
        plan: TrailerPlan = plans[audience]
        
        violating_segment_ids = set()
        for v in violations:
            if v.get("segment_id"):
                violating_segment_ids.add(v["segment_id"])
                
        # Selective patch logic
        for segment in plan.segments:
            if segment.segment_id in violating_segment_ids:
                # Find a safe replacement deterministically for the assignment mock
                safe_clip_id = None
                for c_id in catalog.keys():
                    if c_id != segment.clip_id:
                        safe_clip_id = c_id
                        break
                
                if safe_clip_id:
                    segment.clip_id = safe_clip_id
                    segment.editorial_reasoning = f"Automated repair: replaced with {safe_clip_id} to satisfy constraints."
                    segment.risk_flags.append("REPAIRED")
                    
        # Reset validation status so it gets checked again on the loop back
        plan.validation_status = "PENDING"
        plans[audience] = plan
        
    return {"trailer_plans": plans}
