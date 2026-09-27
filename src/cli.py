import argparse
import json
import os
from src.graph.workflow import build_workflow
from src.graph.state import GraphState

def run_pipeline(episode_path: str, contracts_path: str, policies_path: str, mode: str):
    print(f"--- Starting Autonomous Trailer Director ({mode} MODE) ---")
    
    # 1. Initialize State
    episode_manifest = {"scenes": []}
    if os.path.exists(episode_path):
        with open(episode_path, "r", encoding="utf-8") as f:
            episode_manifest = json.load(f)
            
    state = GraphState(
        raw_episode_manifest=episode_manifest,
        candidate_catalog={},
        constraint_matrix=[],
        protected_facts=[],
        trailer_plans={},
        validation_reports={},
        repair_attempts={},
        accumulated_cost_usd=0.0,
        budget_limit_usd=5.0,
        runtime_mode=mode
    )
    
    # 2. Build and Execute Graph
    app = build_workflow()
    print("Executing workflow...")
    
    # Run the LangGraph application
    final_state = app.invoke(state)
    
    print("\n--- Pipeline Execution Complete ---")
    reports = final_state.get("validation_reports", {})
    plans = final_state.get("trailer_plans", {})
    
    for audience, plan in plans.items():
        status = plan.validation_status
        print(f"[{audience.upper()}] Final Status: {status} | Segments: {len(plan.segments)}")
        if status == "FAIL":
            print(f"   -> Unresolved Violations: {reports.get(audience)}")
            
    # Generate validation_report.md
    report_lines = ["# Validation Report\n"]
    for aud, plan in final_state.get("trailer_plans", {}).items():
        report_lines.append(f"## {aud.upper()} Trailer")
        report_lines.append(f"- Status: {plan.validation_status}")
        flags = final_state.get("validation_reports", {}).get(aud, [])
        if flags:
            report_lines.append(f"- Violations encountered: {len(flags)}")
            for v in flags:
                report_lines.append(f"  - [{v.get('type')}] Segment {v.get('segment_id')}: {v.get('reasoning', '')}")
        else:
            report_lines.append("- Clean pass. No violations.")
        report_lines.append("")
        
    os.makedirs("sample_run", exist_ok=True)
    with open("sample_run/validation_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\nCheck the 'sample_run/' directory for output EDLs and Quarantines.")

def simulate_event(event_type: str, asset_id: str, input_run: str):
    print(f"Simulating event: {event_type} on {asset_id}")
    # Hook for testing surprise events like CONTRACT_REVOKED
    print("Event simulated. Impact analyzer would re-run here.")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Trailer Director CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    run_parser = subparsers.add_parser("run", help="Run end-to-end multi-audience generation")
    run_parser.add_argument("--episode", default="data/sample_episode.json")
    run_parser.add_argument("--contracts", default="data/contracts.json")
    run_parser.add_argument("--policies", default="data/policies.json")
    run_parser.add_argument("--mode", default="MOCK", choices=["LIVE", "MOCK", "FALLBACK"])
    
    sim_parser = subparsers.add_parser("simulate-event", help="Run surprise-event impact simulation")
    sim_parser.add_argument("--type", required=True)
    sim_parser.add_argument("--asset-id", required=True)
    sim_parser.add_argument("--input-run", required=True)
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_pipeline(args.episode, args.contracts, args.policies, args.mode)
    elif args.command == "simulate-event":
        simulate_event(args.type, args.asset_id, args.input_run)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
