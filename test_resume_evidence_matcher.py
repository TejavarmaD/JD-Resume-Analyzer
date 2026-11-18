
from resume_evidence_matcher import (
    evaluate_non_tag_requirement,
    evaluate_requirement,
    apply_manual_evidence,
)

def test_req_068_monitoring_confirmation_does_not_satisfy_deployment():
    requirement = {
        "requirement_id": "REQ-068",
        "requirement_text": "Monitoring and deployment of AI applications.",
        "skill_tags": {},
    }

    # No resume evidence is available for either group.
    evaluation = evaluate_requirement(requirement, segments=[])

    manual_data = {
        "REQ-068": {
            "requirement_text": "Monitoring and deployment of AI applications.",
            "status": "partial",
            "confirmation": (
                "Monitoring and improvement of AI agents was confirmed. "
                "Application deployment was not confirmed."
            ),
            "evidence": [
                {
                    "project": "Omni AI agents",
                    "claim": "Monitored and improved the AI agents.",
                    "evidence_group": "application monitoring",
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation,
        "REQ-068",
        manual_data,
    )

    groups = {
        group["label"]: group
        for group in result["evidence_groups"]
    }

    # Overall requirement must remain partial.
    assert result["status"] == "partial"
    assert result["resume_status"] == "missing"
    assert result["manual_status"] == "partial"

    # Monitoring is satisfied by manual confirmation.
    assert groups["application monitoring"]["status"] == "matched"
    assert groups["application monitoring"]["satisfied"] is True
    assert groups["application monitoring"]["manual_evidence_count"] == 1

    # Deployment must remain unsatisfied.
    assert groups["application deployment"]["status"] == "missing"
    assert groups["application deployment"]["satisfied"] is False
    assert groups["application deployment"]["manual_evidence"] == []
    assert groups["application deployment"]["manual_evidence_count"] == 0

    # Manual confirmation must not become resume evidence.
    assert result["evidence"] == []
    assert result["manual_evidence"][0]["evidence_source"] == "user_confirmed"


def test_req_031_partial_manual_confirmation_does_not_become_matched():
    evaluation = {
        "requirement_text": "Provide technical documentation, participate in code reviews and technical discussions.",
        "status": "missing",
        "status_reason": "No evidence found.",
        "evidence_strength": "none",
        "evidence_groups": [
            {
                "label": "technical documentation",
                "status": "missing",
                "satisfied": False,
                "evidence_count": 0,
                "evidence": [],
                "manual_evidence": [],
                "manual_evidence_count": 0,
            }
        ],
        "evidence": [],
    }

    manual_data = {
        "REQ-031": {
            "requirement_text": "Provide technical documentation, participate in code reviews and technical discussions.",
            "status": "partial",
            "confirmation": (
                "Technical documentation confirmed. "
                "Code reviews and technical discussions are not confirmed."
            ),
            "evidence": [
                {
                    "project": "Professional work",
                    "claim": "Prepared technical documentation.",
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation, "REQ-031", manual_data
    )

    assert result["status"] == "partial"
    assert result["resume_status"] == "missing"
    assert result["manual_status"] == "partial"
    assert result["manual_evidence"][0]["evidence_source"] == "user_confirmed"
    assert result["evidence"] == []


def test_req_035_missing_manual_confirmation_does_not_satisfy_requirement():
    evaluation = {
        "requirement_text": "Integrate external LLM APIs into personal applications.",
        "status": "partial",
        "status_reason": "LLM evidence found, API integration not established.",
        "evidence_strength": "partial",
        "evidence_groups": [],
        "evidence": [{"claim": "Used an LLM interface."}],
    }

    manual_data = {
        "REQ-035": {
            "requirement_text": "Integrate external LLM APIs into personal applications.",
            "status": "missing",
            "confirmation": (
                "Used the Omni AI interface. External LLM API integration "
                "within a personal application was not confirmed."
            ),
            "evidence": [
                {
                    "project": "Omni AI",
                    "claim": "Used the Omni AI interface; no personal API integration confirmed.",
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation, "REQ-035", manual_data
    )

    assert result["status"] == "missing"
    assert result["resume_status"] == "partial"
    assert result["manual_status"] == "missing"
    assert result["evidence"] == [{"claim": "Used an LLM interface."}]
    assert result["manual_evidence"][0]["evidence_source"] == "user_confirmed"


def test_req_058_matched_manual_confirmation_is_separate_from_resume_evidence():
    evaluation = {
        "requirement_text": "Analyze data and investigate business problems.",
        "status": "missing",
        "status_reason": "No evidence found.",
        "evidence_strength": "none",
        "evidence_groups": [],
        "evidence": [],
    }

    manual_data = {
        "REQ-058": {
            "requirement_text": "Analyze data and investigate business problems.",
            "status": "matched",
            "confirmation": "Revenue Insights project details were confirmed.",
            "evidence": [
                {
                    "project": "Revenue Insights — AtliQ Grands",
                    "actions": [
                        "Analyzed more than 100,000 booking records using Power BI."
                    ],
                    "reported_outcomes": [
                        "12% improvement in peak utilization."
                    ],
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation, "REQ-058", manual_data
    )

    assert result["status"] == "matched"
    assert result["resume_status"] == "missing"
    assert result["manual_status"] == "matched"
    assert result["evidence"] == []
    assert result["manual_evidence"][0]["evidence_source"] == "user_confirmed"
    assert result["evidence_strength"] == "user_confirmed"


def test_manual_evidence_without_group_applies_to_single_group_only():
    evaluation = {
        "requirement_text": "Provide technical documentation.",
        "status": "missing",
        "status_reason": "No evidence found.",
        "evidence_strength": "none",
        "evidence_groups": [
            {
                "label": "technical documentation",
                "status": "missing",
                "satisfied": False,
                "evidence_count": 0,
                "evidence": [],
                "manual_evidence": [],
                "manual_evidence_count": 0,
            }
        ],
        "evidence": [],
    }

    manual_data = {
        "REQ-031": {
            "requirement_text": "Provide technical documentation.",
            "status": "matched",
            "confirmation": "Technical documentation confirmed.",
            "evidence": [
                {
                    "project": "Professional work",
                    "claim": "Prepared technical documentation.",
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation, "REQ-031", manual_data
    )

    group = result["evidence_groups"][0]

    assert result["status"] == "matched"
    assert group["status"] == "matched"
    assert group["manual_evidence_count"] == 1

def test_live_router_preserves_req_068_manual_evidence_groups():
    requirement = {
        "requirement_id": "REQ-068",
        "requirement_text": "Monitoring and deployment of AI applications.",
        "skill_tags": {},
        "alternatives": [],
        "unmatched_terms": [],
    }

    manual_data = {
        "REQ-068": {
            "requirement_text": "Monitoring and deployment of AI applications.",
            "status": "partial",
            "confirmation": "Monitoring experience confirmed.",
            "evidence": [
                {
                    "project": "Omni AI agents",
                    "claim": "Monitored and improved the AI agents.",
                    "evidence_group": "application monitoring",
                }
            ],
        }
    }

    evaluation = evaluate_requirement(
        requirement,
        segments=[],
    )

    labels = {
        group["label"]
        for group in evaluation["evidence_groups"]
    }

    assert labels == {
        "application deployment",
        "application monitoring",
    }

    result = apply_manual_evidence(
        evaluation,
        "REQ-068",
        manual_data,
    )

    monitoring_group = next(
        group
        for group in result["evidence_groups"]
        if group["label"] == "application monitoring"
    )

    deployment_group = next(
        group
        for group in result["evidence_groups"]
        if group["label"] == "application deployment"
    )

    assert monitoring_group["status"] == "matched"
    assert deployment_group["status"] == "missing"
    assert result["status"] == "partial"

def test_missing_manual_confirmation_does_not_satisfy_single_evidence_group():
    evaluation = {
        "requirement_text": "Integrate external model APIs into an application.",
        "status": "partial",
        "status_reason": "Related LLM evidence found, API integration not established.",
        "evidence_strength": "partial",
        "evidence_groups": [
            {
                "label": "Integrate external model APIs",
                "status": "partial",
                "satisfied": False,
                "evidence_count": 2,
                "evidence": [
                    {"claim": "Developed AI agents on an internal LLM platform."}
                ],
                "manual_evidence": [],
                "manual_evidence_count": 0,
            }
        ],
        "evidence": [
            {"claim": "Developed AI agents on an internal LLM platform."}
        ],
    }

    manual_data = {
        "TEST-API-001": {
            "requirement_text": "Integrate external model APIs into an application.",
            "status": "missing",
            "confirmation": "External API integration was not confirmed.",
            "evidence": [
                {
                    "project": "Internal AI platform",
                    "claim": "Used the platform interface; API integration not confirmed.",
                }
            ],
        }
    }

    result = apply_manual_evidence(
        evaluation, "TEST-API-001", manual_data
    )

    assert result["status"] == "partial"
    assert result["resume_status"] == "partial"
    assert result["manual_status"] == "missing"
    assert result["evidence_groups"][0]["status"] == "partial"
    assert result["evidence_groups"][0]["satisfied"] is False
    assert result["evidence_groups"][0]["manual_evidence"] == []
    assert len(result["manual_evidence"]) == 1

def test_manual_evidence_with_mismatched_requirement_text_is_rejected():
    evaluation = {
        "requirement_text": "Develop and maintain financial forecasts.",
        "status": "missing",
        "evidence": [],
    }
    manual_data = {
        "REQ-010": {
            "requirement_text": "Prepare monthly financial forecasts.",
            "status": "matched",
            "confirmation": "Confirmed experience preparing forecasts.",
            "evidence": [{"claim": "Prepared monthly forecasts."}],
        }
    }

    result = apply_manual_evidence(evaluation, "REQ-010", manual_data)

    assert result["status"] == "missing"
    assert result["resume_status"] == "missing"
    assert result["manual_status"] is None
    assert result["manual_evidence"] == []
    assert result["manual_confirmation"] is None
    assert result["manual_evidence_validation"] == "requirement_text_mismatch"
    assert "was not applied" in result["manual_evidence_warning"]


def test_legacy_manual_evidence_without_requirement_text_is_rejected():
    evaluation = {
        "requirement_text": "Prepare monthly financial forecasts.",
        "status": "partial",
        "evidence": [],
    }
    manual_data = {
        "REQ-010": {
            "status": "matched",
            "confirmation": "Legacy confirmation without bound requirement text.",
            "evidence": [{"claim": "Prepared forecasts."}],
        }
    }

    result = apply_manual_evidence(evaluation, "REQ-010", manual_data)

    assert result["status"] == "partial"
    assert result["resume_status"] == "partial"
    assert result["manual_status"] is None
    assert result["manual_evidence"] == []
    assert result["manual_confirmation"] is None
    assert result["manual_evidence_validation"] == "legacy_unbound"
    assert "was not applied" in result["manual_evidence_warning"]
