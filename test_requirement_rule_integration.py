from requirement_rule_selector import select_requirement_strategy
from resume_evidence_matcher import evaluate_requirement

def test_same_wording_selects_same_strategy_for_different_ids():
    first = {"requirement_id": "REQ-068", "requirement_text": "Monitor deployed applications in production."}
    second = {"requirement_id": "CUSTOM-900", "requirement_text": "Monitor deployed applications in production."}
    assert select_requirement_strategy(first)["strategy"] == select_requirement_strategy(second)["strategy"] == "deployment_monitoring_evidence"

def test_different_wording_does_not_inherit_old_requirement_id_rule():
    requirement = {"requirement_id": "REQ-068", "requirement_text": "Prepare monthly financial forecasts.", "skill_tags": {}}
    result = evaluate_requirement(requirement, [])
    assert result["evaluation_method"] == "generic_requirement_evidence_matching"
    assert result["rule_selection"]["strategy"] == "generic_requirement_evidence_matching"

def test_technical_communication_rule_selected_from_wording():
    requirement = {"requirement_id": "ANY-ID", "requirement_text": "Create technical documentation and deliver knowledge transfer sessions.", "skill_tags": {}}
    result = evaluate_requirement(requirement, [])
    assert result["evaluation_method"] == "technical_communication_evidence"

def test_tag_policy_selected_without_requirement_id():
    requirement = {
        "requirement_id": "ANY-ID",
        "requirement_text": "Integrate external model APIs into an application.",
        "skill_tags": {
            "concepts": [],
            "technologies": [],
            "platforms": [{"tag": "openai"}],
            "standards": [],
        },
    }
    result = evaluate_requirement(requirement, [])
    assert result["evaluation_method"] == "model_api_integration_evidence"

def test_generic_fallback_is_role_agnostic():
    requirement = {"requirement_id": "REQ-010", "requirement_text": "Prepare monthly financial forecasts.", "skill_tags": {}}
    result = evaluate_requirement(requirement, [])
    assert result["rule_selection"]["strategy"] == "generic_requirement_evidence_matching"


def test_every_selected_strategy_maps_to_exactly_one_evaluator_registry():
    from requirement_rule_selector import RULE_PATTERNS
    from resume_evidence_matcher import (
        NON_TAG_EVIDENCE_RULES,
        SPECIAL_REQUIREMENT_RULES,
        REQUIREMENT_TAG_POLICIES,
    )

    registries = (
        NON_TAG_EVIDENCE_RULES,
        SPECIAL_REQUIREMENT_RULES,
        REQUIREMENT_TAG_POLICIES,
    )
    selected_strategies = {strategy for strategy, _ in RULE_PATTERNS}

    for strategy in selected_strategies:
        matching_registries = [
            registry for registry in registries
            if strategy in registry
        ]
        assert len(matching_registries) == 1, (
            f"Strategy {strategy!r} must exist in exactly one evaluator registry."
        )
