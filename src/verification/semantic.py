import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from src.graph.state import GraphState, TrailerPlan
from src.gateway.model_gateway import ModelGateway

class SemanticViolation(BaseModel):
    segment_id: str
    violation_type: str = Field(description="E.g., SPOILER_LEAK, TONE_MISMATCH, CULTURAL_STEREOTYPE")
    reasoning: str

class SemanticReport(BaseModel):
    violations: List[SemanticViolation]

class SemanticVerifier:
    """
    Tier 2: Semantic Verification (Targeted LLM Evaluators)
    Evaluates semantic constraints like spoilers, tone, and cultural respect.
    """
    @staticmethod
    def verify_plan(plan: TrailerPlan, state: GraphState) -> List[Dict[str, Any]]:
        gateway = ModelGateway(mode=state.get("runtime_mode", "LIVE"), cost_limit=state.get("budget_limit_usd", 5.0))
        protected_facts = state.get("protected_facts", [])
        
        # We enforce specific logical bounds per audience map
        prompt = ""
        mock_data = {"violations": []}
        
        if plan.audience == "young_adult":
            spoilers = [f for f in protected_facts if f.get('is_spoiler')]
            prompt = f"""
            Analyze this trailer plan and ensure it does NOT reveal any protected spoilers.
            Protected Spoilers: {json.dumps(spoilers)}
            Plan Segments: {json.dumps([s.model_dump() for s in plan.segments])}
            """
            
        elif plan.audience == "dialect_region":
            prompt = f"""
            Analyze the trailer for cultural respect. Flag any dialect misuse or stereotyping.
            Plan Segments: {json.dumps([s.model_dump() for s in plan.segments])}
            """
            
        else:
            # For family, tone/rating checks
            prompt = f"""
            Analyze the trailer for 'Family' rating compliance (no violence, high tension).
            Plan Segments: {json.dumps([s.model_dump() for s in plan.segments])}
            """
            
        report = gateway.generate(prompt=prompt, schema=SemanticReport, mock_data=mock_data)
        
        return [v.model_dump() for v in report.violations]

def tier2_semantic_node(state: GraphState) -> GraphState:
    """Stage 3 - Tier 2 Node"""
    reports = state.get("validation_reports", {})
    plans = state.get("trailer_plans", {})
    
    new_reports = {}
    for audience, plan in plans.items():
        existing_violations = reports.get(audience, [])
        semantic_violations = SemanticVerifier.verify_plan(plan, state)
        
        # Append semantic violations directly onto deterministic ones
        for sv in semantic_violations:
            existing_violations.append({
                "type": sv.get("violation_type", "SEMANTIC_ERROR"),
                "segment_id": sv.get("segment_id"),
                "detail": sv.get("reasoning")
            })
            
        new_reports[audience] = existing_violations
        
    return {"validation_reports": new_reports}
