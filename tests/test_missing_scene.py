from src.graph.state import TrailerPlan, PlannedSegment, GraphState
from src.verification.deterministic import DeterministicVerifier

def test_missing_scene_raises_error():
    """
    Test that referencing a hallucinated clip_id (C999) fails Deterministic Verification.
    """
    plan = TrailerPlan(
        trailer_id="test_plan",
        audience="family",
        duration_seconds=30,
        audience_promise="Test",
        total_cost_usd=0,
        validation_status="PENDING",
        segments=[
            PlannedSegment(
                segment_id="seg_01",
                clip_id="C999", # Hallucinated ID
                audio_track_id="music_01",
                narrative_function="Hook",
                editorial_reasoning="Test",
                cited_evidence=[]
            )
        ]
    )
    
    state = GraphState(candidate_catalog={}, constraint_matrix=[])
    violations = DeterministicVerifier.verify_plan(plan, state)
    
    assert len(violations) == 1
    assert violations[0]["type"] == "MISSING_ASSET"
    assert "C999" in violations[0]["detail"]
