from typing import Dict, List, Any
from src.graph.state import GraphState

def impact_analyzer_node(state: GraphState) -> GraphState:
    """
    Stage 4a: Impact Analyzer
    Pinpoints the exact index of the failing segment based on validation reports.
    """
    reports = state.get("validation_reports", {})
    repair_attempts = state.get("repair_attempts", {}).copy()
    
    for audience, violations in reports.items():
        if len(violations) > 0:
            current_attempts = repair_attempts.get(audience, 0)
            repair_attempts[audience] = current_attempts + 1
            
    return {"repair_attempts": repair_attempts}
