import pytest
from src.graph.state import TrailerPlan, PlannedSegment, GraphState
from src.verification.semantic import SemanticVerifier

def test_spoiler_detection_blocks_twist_in_young_adult(monkeypatch):
    """
    Test that the semantic AI engine catches a spoiler in the Young Adult cut.
    """
    plan = TrailerPlan(
        trailer_id="test", audience="young_adult", duration_seconds=30,
        audience_promise="Test", total_cost_usd=0, validation_status="PENDING",
        segments=[PlannedSegment(segment_id="seg_01", clip_id="C002", audio_track_id="music_01", narrative_function="Hook", editorial_reasoning="Test", cited_evidence=[])]
    )
    
    state = GraphState(
        protected_facts=[{"fact_id": "Fact_02", "description": "The twist.", "linked_scene_ids": ["scene_02"], "is_spoiler": True}],
        budget_limit_usd=5.0, runtime_mode="MOCK"
    )
    
    # Mocking the LLM gateway returning a spoiler violation
    class MockGateway:
        def __init__(self, mode, cost_limit): pass
        def generate(self, prompt, schema, mock_data):
            from src.verification.semantic import SemanticReport, SemanticViolation
            return SemanticReport(violations=[SemanticViolation(segment_id="seg_01", violation_type="SPOILER_LEAK", reasoning="Revealed twist.")])

    import src.verification.semantic as sem
    monkeypatch.setattr(sem, "ModelGateway", MockGateway)

    violations = SemanticVerifier.verify_plan(plan, state)
    
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "SPOILER_LEAK"
