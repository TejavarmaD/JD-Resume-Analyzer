
from resume_evidence_matcher import (
    evaluate_non_tag_requirement,
    apply_manual_evidence,
)


def test_req_068_monitoring_confirmation_does_not_satisfy_deployment():
    requirement = {
        "requirement_id": "REQ-068",
    }

    # No resume evidence is available for either group.
    evaluation = evaluate_non_tag_requirement(
        requirement,
        segments=[],
    )

    manual_data = {
        "REQ-068": {
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
        "status": "partial",
        "status_reason": "LLM evidence found, API integration not established.",
        "evidence_strength": "partial",
        "evidence_groups": [],
        "evidence": [{"claim": "Used an LLM interface."}],
    }

    manual_data = {
        "REQ-035": {
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
        "status": "missing",
        "status_reason": "No evidence found.",
        "evidence_strength": "none",
        "evidence_groups": [],
        "evidence": [],
    }

    manual_data = {
        "REQ-058": {
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

