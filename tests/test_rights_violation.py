from src.graph.state import TrailerPlan, PlannedSegment, CandidateClip, TimecodeSpan, ConstraintRule, GraphState
from src.verification.deterministic import DeterministicVerifier

def test_rights_violation_blocks_actor():
    """
    Test that a trailer plan referencing a blocked actor is correctly rejected.
    """
    plan = TrailerPlan(
        trailer_id="test",
        audience="family",
        duration_seconds=30,
        audience_promise="Test",
        total_cost_usd=0,
        validation_status="PENDING",
        segments=[
            PlannedSegment(
                segment_id="seg_01",
                clip_id="C001",
                audio_track_id="music_01",
                narrative_function="Hook",
                editorial_reasoning="Test",
                cited_evidence=[]
            )
        ]
    )
    
    clip = CandidateClip(
        clip_id="C001",
        scene_id="scene_01",
        timecodes=TimecodeSpan(source_in="00:00:00.000", source_out="00:00:01.000", duration_ms=1000),
        primary_character_ids=["actor_blocked"],
        dialogue_ids=[],
        audio_track_ids=[],
        intensity_score=0.5,
        cultural_context_tags=[],
        has_spoilers=False
    )
    
    rule = ConstraintRule(
        rule_id="rule_1",
        category="RIGHTS",
        target_entity="actor:actor_blocked",
        condition="EQUALS",
        action="BLOCK",
        source_clause="Actor blocked."
    )
    
    state = GraphState(candidate_catalog={"C001": clip}, constraint_matrix=[rule])
    violations = DeterministicVerifier.verify_plan(plan, state)
    
    assert len(violations) == 1
    assert violations[0]["type"] == "RIGHTS_VIOLATION"
    assert "actor_blocked" in violations[0]["detail"]
