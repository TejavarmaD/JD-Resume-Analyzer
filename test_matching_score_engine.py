
import pytest

from matching_score_engine import (
    build_output,
    build_critical_gaps,
    calculate_alignment,
    score_requirement,
)


def make_inputs(
    status="matched",
    priority="must_have",
    base_weight=1.0,
    tag_count=1,
    eligibility_status="unverified",
):
    requirement = {
        "id": "REQ-001",
        "requirement": "Build Python applications.",
        "category": "programming_backend",
        "priority": priority,
        "requirement_type": "skill",
        "base_weight": base_weight,
        "priority_weight": 1.0,
    }

    tag_record = {
        "requirement_id": "REQ-001",
        "requirement_text": requirement["requirement"],
        "skill_tags": {
            "concepts": ["python"] if tag_count else [],
            "technologies": ["python"] * max(0, tag_count - 1),
            "platforms": [],
            "standards": [],
        },
    }

    evidence_record = {
        "requirement_id": "REQ-001",
        "requirement_text": requirement["requirement"],
        "status": status,
        "evidence_strength": "implementation",
        "evaluation_method": "test",
        "status_reason": "Test evidence.",
        "evidence": [],
        "manual_evidence": [],
        "tag_coverage": {},
    }

    jd_data = {"requirements": [requirement]}
    tag_data = {"requirements": [tag_record]}
    evidence_data = {"requirements": [evidence_record]}
    eligibility_data = {
        "assessment": {
            "eligibility_status": eligibility_status,
        }
    }

    return jd_data, tag_data, evidence_data, eligibility_data


def test_matched_partial_and_missing_point_allocation():
    expected = {
        "matched": (1.0, 1.0),
        "partial": (0.5, 0.5),
        "missing": (0.0, 0.0),
    }

    for status, (expected_points, expected_earned) in expected.items():
        jd, tags, evidence, _ = make_inputs(status=status)

        result = score_requirement(
            jd["requirements"][0],
            tags["requirements"][0],
            evidence["requirements"][0],
        )

        assert result["score_points"] == expected_points
        assert result["earned_weight"] == expected_earned


def test_must_have_and_good_to_have_use_jd_base_weight():
    jd, tags, evidence, _ = make_inputs(
        status="partial",
        priority="must_have",
        base_weight=2.0,
    )

    must_have = score_requirement(
        jd["requirements"][0],
        tags["requirements"][0],
        evidence["requirements"][0],
    )

    jd, tags, evidence, _ = make_inputs(
        status="partial",
        priority="good_to_have",
        base_weight=1.0,
    )

    good_to_have = score_requirement(
        jd["requirements"][0],
        tags["requirements"][0],
        evidence["requirements"][0],
    )

    assert must_have["weight"] == 2.0
    assert good_to_have["weight"] == 1.0

    assert must_have["earned_weight"] == 1.0
    assert good_to_have["earned_weight"] == 0.5

    # Priority must not be multiplied into base_weight again.
    assert must_have["weight"] == 2.0


def test_critical_gaps_exclude_good_to_have_requirements():
    jd, tags, evidence, _ = make_inputs(
        status="missing",
        priority="good_to_have",
    )

    good_to_have = score_requirement(
        jd["requirements"][0],
        tags["requirements"][0],
        evidence["requirements"][0],
    )

    jd, tags, evidence, _ = make_inputs(
        status="partial",
        priority="must_have",
    )

    must_have = score_requirement(
        jd["requirements"][0],
        tags["requirements"][0],
        evidence["requirements"][0],
    )

    gaps = build_critical_gaps([good_to_have, must_have])

    assert len(gaps) == 1
    assert gaps[0]["requirement_id"] == "REQ-001"
    assert gaps[0]["status"] == "partial"


def test_skill_tags_do_not_change_alignment_score():
    jd, tags, evidence, eligibility = make_inputs(
        status="partial",
        tag_count=1,
    )

    output_one_tag = build_output(
        jd, tags, evidence, eligibility
    )

    jd, tags, evidence, eligibility = make_inputs(
        status="partial",
        tag_count=5,
    )

    output_five_tags = build_output(
        jd, tags, evidence, eligibility
    )

    assert (
        output_one_tag["alignment"]["alignment_score"]
        == output_five_tags["alignment"]["alignment_score"]
    )

    assert (
        output_one_tag["requirements"][0]["earned_weight"]
        == output_five_tags["requirements"][0]["earned_weight"]
    )

    assert (
        output_one_tag["requirements"][0]["tag_count"]
        != output_five_tags["requirements"][0]["tag_count"]
    )

    assert (
        output_one_tag["scoring_policy"]["skill_tags_are_diagnostic_only"]
        is True
    )


def test_experience_eligibility_is_separate_from_alignment_score():
    jd, tags, evidence, eligibility = make_inputs(
        status="partial",
        eligibility_status="unverified",
    )

    unverified_output = build_output(
        jd, tags, evidence, eligibility
    )

    jd, tags, evidence, eligibility = make_inputs(
        status="partial",
        eligibility_status="eligible",
    )

    eligible_output = build_output(
        jd, tags, evidence, eligibility
    )

    assert (
        unverified_output["alignment"]["alignment_score"]
        == eligible_output["alignment"]["alignment_score"]
    )

    assert (
        unverified_output["experience_eligibility"]["eligibility_status"]
        == "unverified"
    )

    assert (
        eligible_output["experience_eligibility"]["eligibility_status"]
        == "eligible"
    )

    assert (
        unverified_output["scoring_policy"]["experience_eligibility_is_separate"]
        is True
    )


def test_rejects_mismatched_requirement_ids():
    jd, tags, evidence, eligibility = make_inputs()

    tags["requirements"][0]["requirement_id"] = "REQ-999"

    with pytest.raises(
        ValueError,
        match="requirement IDs do not match",
    ):
        build_output(jd, tags, evidence, eligibility)


def test_rejects_mismatched_requirement_text():
    jd, tags, evidence, eligibility = make_inputs()

    evidence["requirements"][0]["requirement_text"] = (
        "Build Java applications."
    )

    with pytest.raises(
        ValueError,
        match="Requirement text mismatch in evidence",
    ):
        build_output(jd, tags, evidence, eligibility)


def test_calculate_alignment_uses_weighted_earned_points():
    requirements = [
        {
            "weight": 2.0,
            "earned_weight": 2.0,
        },
        {
            "weight": 1.0,
            "earned_weight": 0.5,
        },
        {
            "weight": 1.0,
            "earned_weight": 0.0,
        },
    ]

    result = calculate_alignment(requirements)

    assert result["total_weight"] == 4.0
    assert result["earned_weight"] == 2.5
    assert result["alignment_score"] == 62.5
