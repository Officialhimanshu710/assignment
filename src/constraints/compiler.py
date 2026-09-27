import json
from pathlib import Path
from typing import List, Dict, Any
from src.graph.state import ConstraintRule, GraphState

class ConstraintCompiler:
    """
    Stage 1.5: Constraint Compiler (Deterministic Python)
    Transforms contracts & rating rules into binary ConstraintRules.
    Pre-calculates blocklists for rights violations.
    """
    
    @classmethod
    def compile_rules(cls, policies_data: Dict[str, Any], contracts_data: Dict[str, Any]) -> List[ConstraintRule]:
        rules: List[ConstraintRule] = []
        
        contracts = contracts_data.get("contracts", [])
        for contract in contracts:
            entity = contract.get("entity", "")
            if contract.get("status") == "EXPIRED":
                rules.append(ConstraintRule(
                    rule_id=f"rights_{entity}",
                    category="RIGHTS",
                    target_entity=f"track:{entity}" if "music" in entity else f"actor:{entity}",
                    condition="EQUALS",
                    action="BLOCK",
                    source_clause=contract.get("clause", "Contract Expired")
                ))
            elif contract.get("promotional_use") is False:
                rules.append(ConstraintRule(
                    rule_id=f"promo_{entity}",
                    category="RIGHTS",
                    target_entity=f"actor:{entity}",
                    condition="EQUALS",
                    action="BLOCK",
                    source_clause="No promotional use allowed."
                ))
                
        policies = policies_data.get("policies", [])
        for policy in policies:
            rules.append(ConstraintRule(
                rule_id=policy.get("policy_id", "pol_unknown"),
                category=policy.get("category", "RATING"),
                target_entity=policy.get("target", "global"),
                condition=policy.get("condition", "EXCEEDS_THRESHOLD"),
                action=policy.get("action", "WARN"),
                source_clause=policy.get("description", "")
            ))
            
        return rules

def constraint_compiler_node(state: GraphState) -> GraphState:
    """LangGraph node for compiling constraints deterministically."""
    policies_path = Path("data/policies.json")
    contracts_path = Path("data/contracts.json")
    
    policies_text = policies_path.read_text().strip() if policies_path.exists() else ""
    contracts_text = contracts_path.read_text().strip() if contracts_path.exists() else ""
    
    policies = json.loads(policies_text) if policies_text else {"policies": []}
    contracts = json.loads(contracts_text) if contracts_text else {"contracts": []}
    
    compiled_matrix = ConstraintCompiler.compile_rules(policies, contracts)
    
    # Emit constraint_map.json to disk
    output_path = Path("sample_run/constraint_map.json")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps([c.model_dump() for c in compiled_matrix], indent=2))
    
    return {
        "constraint_matrix": compiled_matrix
    }
