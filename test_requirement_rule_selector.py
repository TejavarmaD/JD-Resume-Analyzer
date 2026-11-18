from requirement_rule_selector import select_requirement_strategy

def test_requirement_id_is_not_a_routing_signal():
    req_a = {"requirement_id": "REQ-068", "requirement_text": "Prepare monthly financial forecasts."}
    req_b = {"requirement_id": "REQ-010", "requirement_text": "Prepare monthly financial forecasts."}
    assert select_requirement_strategy(req_a) == select_requirement_strategy(req_b)
    assert select_requirement_strategy(req_a)["strategy"] == "generic_requirement_evidence_matching"

def test_same_rule_selected_for_different_ids():
    req_a = {"requirement_id": "REQ-068", "requirement_text": "Monitor deployed applications in production."}
    req_b = {"requirement_id": "CUSTOM-123", "requirement_text": "Monitor deployed applications in production."}
    assert select_requirement_strategy(req_a)["strategy"] == "deployment_monitoring_evidence"
    assert select_requirement_strategy(req_b)["strategy"] == "deployment_monitoring_evidence"

def test_role_agnostic_examples():
    examples = {
        "Prepare monthly financial forecasts.": "generic_requirement_evidence_matching",
        "Conduct root cause analysis of operational issues.": "analytical_problem_solving_evidence",
        "Prepare technical documentation and deliver knowledge transfer.": "technical_communication_evidence",
        "Hold a bachelor's degree in computer science.": "education_evidence",
    }
    for requirement_text, expected in examples.items():
        assert select_requirement_strategy({"requirement_text": requirement_text})["strategy"] == expected

def test_tags_are_supporting_selection_signals():
    requirement = {
        "requirement_text": "Integrate external model APIs into an application.",
        "skill_tags": {"platforms": [{"tag": "openai"}]},
    }
    assert select_requirement_strategy(requirement)["strategy"] == "model_api_integration_evidence"

def test_unknown_requirement_uses_generic_strategy():
    result = select_requirement_strategy({"requirement_id": "REQ-068", "requirement_text": "Manage annual vendor budgets."})
    assert result["strategy"] == "generic_requirement_evidence_matching"
    assert result["matched_by"] == "generic_fallback"


def test_statistical_analysis_uses_generic_evaluator():
    requirement = {
        "requirement_text": "Conduct statistical analysis and prepare business reports.",
        "skill_tags": {},
    }
    result = select_requirement_strategy(requirement)
    assert result["strategy"] == "generic_requirement_evidence_matching"
