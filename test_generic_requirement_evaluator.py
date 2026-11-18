
from resume_evidence_matcher import evaluate_requirement


def make_segment(text, section="WORK EXPERIENCE"):
    return {
        "text": text,
        "section": section,
        "record": 0,
        "field": "description",
    }


def make_requirement(text):
    return {
        "requirement_id": "TEST-001",
        "requirement_text": text,
        "skill_tags": {},
        "alternatives": [],
        "unmatched_terms": [],
    }


def test_product_management_requirement_uses_business_evidence():
    requirement = make_requirement(
        "Manage product roadmaps and prioritize product features."
    )

    segments = [
        make_segment(
            "Managed product roadmaps and prioritized product features "
            "based on customer feedback."
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "matched"
    assert result["evaluation_method"] == (
        "generic_requirement_evidence_matching"
    )
    assert result["evidence"]


def test_data_analysis_requirement_uses_analytical_evidence():
    requirement = make_requirement(
        "Analyze business performance and develop reports."
    )

    segments = [
        make_segment(
            "Analyzed business performance and developed reports "
            "for management review."
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "matched"
    assert result["evidence"]


def test_ai_api_integration_does_not_match_platform_familiarity():
    requirement = make_requirement(
        "Integrate external model APIs into production applications."
    )

    segments = [
        make_segment(
            "Used an LLM platform to explore generative AI capabilities."
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "missing"


def test_requirement_without_skill_tags_is_still_evaluated():
    requirement = make_requirement(
        "Conduct statistical analysis and prepare business reports."
    )

    segments = [
        make_segment(
            "Conducted statistical analysis and prepared business reports."
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "matched"
    assert result["tag_coverage"]["total_tags"] == 0


def test_knowledge_only_evidence_is_partial_for_practical_requirement():
    requirement = make_requirement(
        "Develop and maintain data pipelines."
    )

    segments = [
        make_segment(
            "Knowledge of data pipelines and data processing.",
            section="SKILLS",
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "partial"


def test_missing_requirement_remains_missing():
    requirement = make_requirement(
        "Manage financial forecasting and budget planning."
    )

    segments = [
        make_segment(
            "Developed Python applications and REST APIs."
        )
    ]

    result = evaluate_requirement(requirement, segments)

    assert result["status"] == "missing"


def test_evidence_retains_original_source_and_offsets():
    source = (
        "Analyzed business performance and developed reports "
        "for management review."
    )

    requirement = make_requirement(
        "Analyze business performance and develop reports."
    )

    result = evaluate_requirement(
        requirement,
        [make_segment(source)],
    )

    assert result["status"] == "matched"

    for item in result["evidence"]:
        start = item["evidence"]["start"]
        end = item["evidence"]["end"]

        assert item["source_text"] == source
        assert source[start:end] == item["matched_text"]
