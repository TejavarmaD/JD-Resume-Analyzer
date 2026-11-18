import json
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "jd_results"

JD_FILE = OUTPUT_DIR / "ai_engineer_jd_analysis.json"
SKILL_TAG_FILE = OUTPUT_DIR / "ai_engineer_jd_skill_tags.json"
EVIDENCE_FILE = OUTPUT_DIR / "ai_engineer_jd_docx_evidence_match.json"
ELIGIBILITY_FILE = OUTPUT_DIR / "experience_eligibility.json"

OUTPUT_FILE = OUTPUT_DIR / "ai_engineer_jd_docx_match_score.json"

STATUS_POINTS = {
    "matched": 1.0,
    "partial": 0.5,
    "missing": 0.0,
}


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(f"Required input file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_inputs(jd_data, tag_data, evidence_data, eligibility_data):
    jd_requirements = jd_data.get("requirements")
    tag_requirements = tag_data.get("requirements")
    evidence_requirements = evidence_data.get("requirements")

    for name, records in (
        ("JD", jd_requirements),
        ("Skill tags", tag_requirements),
        ("Evidence", evidence_requirements),
    ):
        if not isinstance(records, list):
            raise ValueError(f"{name} requirements must be a list.")

    def build_index(records, id_field):
        indexed = {}
        for record in records:
            requirement_id = record.get(id_field)
            if not requirement_id:
                raise ValueError(f"{id_field} missing from a requirement.")

            if requirement_id in indexed:
                raise ValueError(f"Duplicate requirement ID: {requirement_id}")

            indexed[requirement_id] = record
        return indexed

    jd_index = build_index(jd_requirements, "id")
    tag_index = build_index(tag_requirements, "requirement_id")
    evidence_index = build_index(evidence_requirements, "requirement_id")

    expected_ids = set(jd_index)

    if set(tag_index) != expected_ids:
        raise ValueError("JD and skill-tag requirement IDs do not match.")

    if set(evidence_index) != expected_ids:
        raise ValueError("JD and evidence requirement IDs do not match.")

    for requirement_id, jd_record in jd_index.items():
        if (
            tag_index[requirement_id].get("requirement_text")
            != jd_record.get("requirement")
        ):
            raise ValueError(
                f"Requirement text mismatch in skill tags: {requirement_id}"
            )

        if (
            evidence_index[requirement_id].get("requirement_text")
            != jd_record.get("requirement")
        ):
            raise ValueError(
                f"Requirement text mismatch in evidence: {requirement_id}"
            )

    assessment = eligibility_data.get("assessment")
    if not isinstance(assessment, dict):
        raise ValueError("Experience eligibility assessment is missing.")

    return jd_index, tag_index, evidence_index


def get_tag_coverage(tag_record):
    skill_tags = tag_record.get("skill_tags", {})
    total = 0

    for category in ("concepts", "technologies", "platforms", "standards"):
        total += len(skill_tags.get(category, []))

    return total


def score_requirement(jd_record, tag_record, evidence_record):
    status = evidence_record.get("status")

    if status not in STATUS_POINTS:
        raise ValueError(
            f"Unknown evidence status for {jd_record['id']}: {status}"
        )

    priority = jd_record.get("priority", "must_have")
    if priority not in ("must_have", "good_to_have"):
        raise ValueError(
            f"Unknown priority for {jd_record['id']}: {priority}"
        )

    category = jd_record.get("category", "uncategorized")

    # The JD analyzer's base_weight already incorporates category
    # and priority weighting. Do not multiply priority_weight again.
    weight = float(jd_record.get("base_weight", 1.0))

    if weight < 0:
        raise ValueError(f"Negative requirement weight: {jd_record['id']}")

    points = STATUS_POINTS[status]
    earned_weight = weight * points

    return {
        "requirement_id": jd_record["id"],
        "requirement": jd_record["requirement"],
        "category": category,
        "priority": priority,
        "requirement_type": jd_record.get("requirement_type"),
        "weight": weight,
        "status": status,
        "evidence_strength": evidence_record.get("evidence_strength"),
        "evaluation_method": evidence_record.get("evaluation_method"),
        "score_points": points,
        "earned_weight": round(earned_weight, 4),
        "tag_count": get_tag_coverage(tag_record),
        "tag_coverage": evidence_record.get("tag_coverage", {}),
        "status_reason": evidence_record.get("status_reason", ""),
        "critical_gap": (
            priority == "must_have" and status != "matched"
        ),
        "evidence": evidence_record.get("evidence", []),
        "manual_evidence": evidence_record.get("manual_evidence", []),
    }


def calculate_alignment(requirements):
    total_weight = sum(item["weight"] for item in requirements)

    if total_weight == 0:
        raise ValueError("Total requirement weight is zero.")

    earned_weight = sum(item["earned_weight"] for item in requirements)

    return {
        "alignment_score": round(earned_weight / total_weight * 100, 2),
        "earned_weight": round(earned_weight, 4),
        "total_weight": round(total_weight, 4),
    }


def build_category_scores(requirements):
    categories = defaultdict(
        lambda: {
            "total_requirements": 0,
            "matched": 0,
            "partial": 0,
            "missing": 0,
            "earned_weight": 0.0,
            "total_weight": 0.0,
        }
    )

    for item in requirements:
        category = categories[item["category"]]
        category["total_requirements"] += 1
        category[item["status"]] += 1
        category["earned_weight"] += item["earned_weight"]
        category["total_weight"] += item["weight"]

    result = {}

    for name, values in categories.items():
        total_weight = values["total_weight"]

        result[name] = {
            **{
                key: values[key]
                for key in (
                    "total_requirements",
                    "matched",
                    "partial",
                    "missing",
                )
            },
            "alignment_score": round(
                values["earned_weight"] / total_weight * 100, 2
            ) if total_weight else 0.0,
            "earned_weight": round(values["earned_weight"], 4),
            "total_weight": round(total_weight, 4),
        }

    return result


def build_critical_gaps(requirements):
    gaps = []

    for item in requirements:
        if item["critical_gap"]:
            gaps.append({
                "requirement_id": item["requirement_id"],
                "requirement": item["requirement"],
                "category": item["category"],
                "status": item["status"],
                "evidence_strength": item["evidence_strength"],
                "reason": item["status_reason"],
            })

    return gaps


def build_summary(requirements):
    counts = Counter(item["status"] for item in requirements)

    must_have = [
        item for item in requirements
        if item["priority"] == "must_have"
    ]

    good_to_have = [
        item for item in requirements
        if item["priority"] == "good_to_have"
    ]

    return {
        "total_requirements": len(requirements),
        "matched": counts["matched"],
        "partial": counts["partial"],
        "missing": counts["missing"],
        "must_have_requirements": len(must_have),
        "must_have_not_fully_matched": sum(
            item["status"] != "matched" for item in must_have
        ),
        "good_to_have_requirements": len(good_to_have),
        "good_to_have_matched": sum(
            item["status"] == "matched" for item in good_to_have
        ),
        "total_tag_occurrences": sum(
            item["tag_count"] for item in requirements
        ),
    }


def build_output(jd_data, tag_data, evidence_data, eligibility_data):
    jd_index, tag_index, evidence_index = validate_inputs(
        jd_data, tag_data, evidence_data, eligibility_data
    )

    scored_requirements = []

    for requirement_id, jd_record in jd_index.items():
        scored_requirements.append(
            score_requirement(
                jd_record,
                tag_index[requirement_id],
                evidence_index[requirement_id],
            )
        )

    alignment = calculate_alignment(scored_requirements)
    eligibility = eligibility_data["assessment"]

    return {
        "schema_version": "1.0",
        "scoring_method": "weighted_requirement_evidence_alignment",
        "sources": {
            "jd_analysis": JD_FILE.name,
            "skill_tags": SKILL_TAG_FILE.name,
            "resume_evidence": EVIDENCE_FILE.name,
            "experience_eligibility": ELIGIBILITY_FILE.name,
        },
        "alignment": {
            **alignment,
            "interpretation": (
                "Evidence-based alignment score. It is not a hiring "
                "probability or a guarantee of role eligibility."
            ),
        },
        "summary": build_summary(scored_requirements),
        "category_scores": build_category_scores(scored_requirements),
        "critical_gaps": build_critical_gaps(scored_requirements),
        "experience_eligibility": eligibility,
        "requirements": scored_requirements,
        "scoring_policy": {
            "matched": 1.0,
            "partial": 0.5,
            "missing": 0.0,
            "weight_source": "JD analysis base_weight",
            "skill_tags_are_diagnostic_only": True,
            "experience_eligibility_is_separate": True,
            "critical_gap_rule": (
                "Every must-have requirement not fully matched "
                "is reported as a critical gap."
            ),
        },
        "limitations": [
            "The score depends on the accuracy and completeness of "
            "the source resume and evidence matcher.",
            "Partial evidence receives half credit as an explicit "
            "scoring policy, not a measured probability.",
            "Experience eligibility is reported separately and "
            "does not change the alignment score.",
            "A high alignment score does not override critical gaps.",
        ],
    }


def main():
    try:
        jd_data = load_json(JD_FILE)
        tag_data = load_json(SKILL_TAG_FILE)
        evidence_data = load_json(EVIDENCE_FILE)
        eligibility_data = load_json(ELIGIBILITY_FILE)

        output = build_output(
            jd_data,
            tag_data,
            evidence_data,
            eligibility_data,
        )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(f"ERROR: {type(error).__name__}: {error}")
        raise SystemExit(1)

    print("MATCHING SCORE ENGINE COMPLETE")
    print("=" * 50)
    print(f"Alignment score : {output['alignment']['alignment_score']}%")
    print(f"Matched         : {output['summary']['matched']}")
    print(f"Partial         : {output['summary']['partial']}")
    print(f"Missing         : {output['summary']['missing']}")
    print(
        "Critical gaps   : "
        f"{len(output['critical_gaps'])}"
    )
    print(
        "Eligibility     : "
        f"{output['experience_eligibility']['eligibility_status']}"
    )
    print(f"Output          : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
