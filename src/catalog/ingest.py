import json
from pathlib import Path
from typing import Dict, Any
from src.graph.state import GraphState
from src.catalog.candidate_builder import CandidateBuilder

def ingest_node(state: GraphState) -> GraphState:
    """
    Stage 1: Ingestion & Candidate Catalog (Deterministic Python)
    Reads raw metadata and indexes immutable Candidate Clips.
    
    This node takes the `raw_episode_manifest` from the state, 
    compiles it deterministically, and updates the `candidate_catalog`.
    """
    raw_manifest = state.get("raw_episode_manifest", {})
    
    # Build the catalog deterministically using our builder
    catalog = CandidateBuilder.build_catalog(raw_manifest)
    
    # Return dictionary that will be merged back into the GraphState
    return {
        "candidate_catalog": catalog
    }

def load_local_manifest(filepath: str) -> Dict[str, Any]:
    """Utility to load the mock manifest data from disk."""
    path = Path(filepath)
    if not path.exists():
        return {"scenes": []}
        
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
