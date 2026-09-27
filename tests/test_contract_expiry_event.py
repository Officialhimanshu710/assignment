from src.graph.state import GraphState, TrailerPlan, PlannedSegment, CandidateClip, TimecodeSpan
from src.repair.impact_analyzer import impact_analyzer_node
from src.repair.replanner import replanner_node

def test_contract_expiry_event_triggers_replanning():
    """
    Simulates a contract expiring and triggering a targeted patch replanner.
    """
    plan = TrailerPlan(
        trailer_id="test", audience="family", duration_seconds=30,
        audience_promise="Test", total_cost_usd=0, validation_status="PENDING",
        segments=[PlannedSegment(segment_id="seg_01", clip_id="C001", audio_track_id="music_03", narrative_function="Hook", editorial_reasoning="Test", cited_evidence=[])]
    )
    
    state = GraphState(
        trailer_plans={"family": plan},
        validation_reports={"family": [{"type": "RIGHTS_VIOLATION", "segment_id": "seg_01"}]},
        candidate_catalog={
            "C001": CandidateClip(clip_id="C001", scene_id="s1", timecodes=TimecodeSpan(source_in="00:00:00.000", source_out="00:00:01.000", duration_ms=1000), primary_character_ids=[], dialogue_ids=[], audio_track_ids=[], intensity_score=0.5, cultural_context_tags=[], has_spoilers=False),
            "C002": CandidateClip(clip_id="C002", scene_id="s2", timecodes=TimecodeSpan(source_in="00:00:00.000", source_out="00:00:01.000", duration_ms=1000), primary_character_ids=[], dialogue_ids=[], audio_track_ids=[], intensity_score=0.5, cultural_context_tags=[], has_spoilers=False)
        },
        repair_attempts={}
    )
    
    # Impact analyzer tracks the failure
    state.update(impact_analyzer_node(state))
    assert state["repair_attempts"]["family"] == 1
    
    # Replanner surgically patches the segment
    state.update(replanner_node(state))
    patched_plan = state["trailer_plans"]["family"]
    
    assert patched_plan.segments[0].clip_id != "C001"
    assert "REPAIRED" in patched_plan.segments[0].risk_flags
