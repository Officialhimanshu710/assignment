from typing import Literal
from src.graph.state import GraphState

def adjudicator_node(state: GraphState) -> Literal["release_gate", "impact_analyzer", "escalation_quarantine"]:
    """
    Adjudication Logic (Conditional Edge).
    Evaluates Validation Matrix and determines the next step in the pipeline.
    """
    reports = state.get("validation_reports", {})
    repair_attempts = state.get("repair_attempts", {})
    
    total_violations = sum(len(violations) for violations in reports.values())
    
    # 1. Clean Pass
    if total_violations == 0:
        return "release_gate"
        
    # 2. Unresolvable Risk (Too many repair loops)
    for audience, violations in reports.items():
        if len(violations) > 0:
            attempts = repair_attempts.get(audience, 0)
            if attempts >= 3:
                return "escalation_quarantine"
                
    # 3. Repairable Violation
    return "impact_analyzer"
