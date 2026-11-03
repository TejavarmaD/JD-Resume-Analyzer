
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
