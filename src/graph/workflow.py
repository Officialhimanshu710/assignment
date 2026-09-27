from langgraph.graph import StateGraph, START, END
from src.graph.state import GraphState

# Import nodes
from src.catalog.ingest import ingest_node
from src.constraints.compiler import constraint_compiler_node
from src.graph.nodes import (
    story_mapper_node,
    planner_family_node,
    planner_young_adult_node,
    planner_dialect_node,
    release_gate_node,
    escalation_quarantine_node
)
from src.verification.deterministic import tier1_deterministic_node
from src.verification.semantic import tier2_semantic_node
from src.verification.adjudicator import adjudicator_node
from src.repair.impact_analyzer import impact_analyzer_node
from src.repair.replanner import replanner_node

def build_workflow() -> StateGraph:
    """Assembles the Autonomous Trailer Director LangGraph workflow."""
    workflow = StateGraph(GraphState)
    
    # 1. Add all nodes
    workflow.add_node("ingestion", ingest_node)
    workflow.add_node("constraint_compiler", constraint_compiler_node)
    workflow.add_node("story_mapper", story_mapper_node)
    
    # Parallel Planners
    workflow.add_node("planner_family", planner_family_node)
    workflow.add_node("planner_young_adult", planner_young_adult_node)
    workflow.add_node("planner_dialect", planner_dialect_node)
    
    # Verification Engine
    workflow.add_node("tier1_verification", tier1_deterministic_node)
    workflow.add_node("tier2_verification", tier2_semantic_node)
    
    # Repair & Release
    workflow.add_node("impact_analyzer", impact_analyzer_node)
    workflow.add_node("replanner", replanner_node)
    workflow.add_node("release_gate", release_gate_node)
    workflow.add_node("escalation_quarantine", escalation_quarantine_node)
    
    # 2. Define edges and routing
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "constraint_compiler")
    workflow.add_edge("constraint_compiler", "story_mapper")
    
    # Branching to parallel planners
    workflow.add_edge("story_mapper", "planner_family")
    workflow.add_edge("story_mapper", "planner_young_adult")
    workflow.add_edge("story_mapper", "planner_dialect")
    
    # Merge planners into Verification
    workflow.add_edge("planner_family", "tier1_verification")
    workflow.add_edge("planner_young_adult", "tier1_verification")
    workflow.add_edge("planner_dialect", "tier1_verification")
    
    workflow.add_edge("tier1_verification", "tier2_verification")
    
    # Adjudicator conditional routing
    workflow.add_conditional_edges(
        "tier2_verification",
        adjudicator_node,
        {
            "release_gate": "release_gate",
            "impact_analyzer": "impact_analyzer",
            "escalation_quarantine": "escalation_quarantine"
        }
    )
    
    # Repair loop
    workflow.add_edge("impact_analyzer", "replanner")
    workflow.add_edge("replanner", "tier1_verification")  # Loop back for re-verification
    
    # End points
    workflow.add_edge("release_gate", END)
    workflow.add_edge("escalation_quarantine", END)
    
    return workflow.compile()
