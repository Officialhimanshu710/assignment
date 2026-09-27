import uuid
from typing import Dict, Any
from src.graph.state import CandidateClip, TimecodeSpan

class CandidateBuilder:
    """
    Deterministically builds the Candidate Catalog from ingested raw data.
    Divorces external raw formats from our internal typed structures.
    """
    
    @staticmethod
    def _parse_timecode_to_ms(tc_str: str) -> int:
        """Helper to convert HH:MM:SS.mmm to milliseconds."""
        # Note: A real implementation would parse the string strictly.
        # This is a stub for the deterministic logic.
        return 5000  

    @classmethod
    def build_catalog(cls, raw_manifest: Dict[str, Any]) -> Dict[str, CandidateClip]:
        """
        Parses raw scenes and slices them into discrete candidate clips.
        Assigns immutable CXXX identifiers for zero-hallucination planning.
        """
        catalog: Dict[str, CandidateClip] = {}
        
        scenes = raw_manifest.get("scenes", [])
        clip_counter = 1
        
        for scene in scenes:
            scene_id = scene.get("scene_id", f"scene_{uuid.uuid4().hex[:6]}")
            
            # Each clip gets an immutable, symbolic identifier (e.g. C001)
            clip_id = f"C{clip_counter:03d}"
            
            tc_in = scene.get("source_in", "00:00:00.000")
            tc_out = scene.get("source_out", "00:00:05.000")
            duration_ms = cls._parse_timecode_to_ms(tc_out) - cls._parse_timecode_to_ms(tc_in)
            
            timecodes = TimecodeSpan(
                source_in=tc_in,
                source_out=tc_out,
                duration_ms=duration_ms
            )
            
            clip = CandidateClip(
                clip_id=clip_id,
                scene_id=scene_id,
                timecodes=timecodes,
                primary_character_ids=scene.get("characters", []),
                dialogue_ids=scene.get("dialogue_lines", []),
                audio_track_ids=scene.get("audio_tracks", []),
                intensity_score=scene.get("intensity", 0.5),
                cultural_context_tags=scene.get("cultural_tags", []),
                has_spoilers=scene.get("has_spoilers", False)
            )
            
            catalog[clip_id] = clip
            clip_counter += 1
            
        return catalog
