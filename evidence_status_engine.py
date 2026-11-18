"""Interpret resume-matcher evidence without changing the matching score."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
INPUT_EVIDENCE = BASE_DIR / "jd_results" / "ai_engineer_jd_docx_evidence_match.json"
INPUT_SCORE = BASE_DIR / "jd_results" / "ai_engineer_jd_docx_match_score.json"
OUTPUT_FILE = BASE_DIR / "jd_results" / "ai_engineer_jd_docx_evidence_status.json"

VALID_MATCH_STATUSES = {"matched", "partial", "missing"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _source_types(record: dict[str, Any]) -> list[str]:
    sources: set[str] = set()

    resume_evidence = record.get("evidence", [])
    if isinstance(resume_evidence, list) and resume_evidence:
        sources.add("resume_documented")

    manual_evidence = record.get("manual_evidence", [])
    if isinstance(manual_evidence, list):
        for item in manual_evidence:
            if not isinstance(item, dict):
                continue
            source = str(item.get("evidence_source", "")).lower()
            source_type = str(item.get("source_type", "")).lower()
            if source == "user_confirmed" or source_type == "manual_confirmation":
                sources.add("user_confirmed")

    return sorted(sources)


def _groups(record: dict[str, Any]) -> tuple[list[str], list[str]]:
    groups = record.get("evidence_groups", [])
    supported: list[str] = []
    unsupported: list[str] = []
    if not isinstance(groups, list):
        return supported, unsupported

    for group in groups:
        if not isinstance(group, dict):
            continue
        label = str(group.get("label", "")).strip()
        if not label:
            continue
        if group.get("satisfied") is True or group.get("status") == "matched":
            supported.append(label)
        else:
            unsupported.append(label)
    return supported, unsupported


def classify_evidence_status(record: dict[str, Any]) -> dict[str, Any]:
    """Map matcher status and evidence provenance to a UI-facing evidence state."""
    match_status = record.get("status")
    if match_status not in VALID_MATCH_STATUSES:
        raise ValueError(f"Unsupported matcher status: {match_status!r}")

    sources = _source_types(record)
    supported_groups, unsupported_groups = _groups(record)
    has_resume_evidence = "resume_documented" in sources
    has_user_confirmation = "user_confirmed" in sources

    if match_status == "matched":
        evidence_status = "confirmed_evidence"
        reason = "The existing matcher considers the requirement sufficiently supported. This is evidence support, not independent verification of capability."
        verification_needed = False
    elif match_status == "partial":
        evidence_status = "partially_supported"
        reason = "Some relevant evidence exists, but the requirement is not fully supported."
        verification_needed = True
    elif sources:
        evidence_status = "unverified"
        reason = "Relevant evidence or a related claim exists, but the requirement is not satisfied by the current matching rules."
        verification_needed = True
    else:
        evidence_status = "no_evidence_found"
        reason = "No relevant resume-documented or user-confirmed evidence was found for this requirement. This does not establish lack of capability."
        verification_needed = True

    if has_resume_evidence and has_user_confirmation:
        source_label = "both"
    elif has_resume_evidence:
        source_label = "resume_documented"
    elif has_user_confirmation:
        source_label = "user_confirmed"
    else:
        source_label = "none"

    return {
        "evidence_status": evidence_status,
        "evidence_sources": sources,
        "evidence_source_summary": source_label,
        "supported_evidence_groups": supported_groups,
        "unsupported_evidence_groups": unsupported_groups,
        "reason": reason,
        "verification_needed": verification_needed,
    }


def build_output(evidence_data: dict[str, Any], score_data: dict[str, Any]) -> dict[str, Any]:
    evidence_records = evidence_data.get("requirements")
    score_records = score_data.get("requirements")
    if not isinstance(evidence_records, list) or not isinstance(score_records, list):
        raise ValueError("Both input files must contain a requirements list.")

    score_by_id = {item.get("requirement_id"): item for item in score_records}
    if len(score_by_id) != len(score_records):
        raise ValueError("Duplicate requirement IDs found in score input.")

    output_records = []
    for evidence_record in evidence_records:
        requirement_id = evidence_record.get("requirement_id")
        score_record = score_by_id.get(requirement_id)
        if score_record is None:
            raise ValueError(f"Requirement missing from score input: {requirement_id}")
        if evidence_record.get("requirement_text") != score_record.get("requirement"):
            raise ValueError(f"Requirement text mismatch for {requirement_id}")

        classification = classify_evidence_status(evidence_record)
        output_records.append({
            "requirement_id": requirement_id,
            "requirement": score_record["requirement"],
            "category": score_record.get("category"),
            "priority": score_record.get("priority"),
            "original_match_status": evidence_record.get("status"),
            "evidence_strength": evidence_record.get("evidence_strength"),
            "original_score_points": score_record.get("score_points"),
            "original_earned_weight": score_record.get("earned_weight"),
            **classification,
        })

    counts = {key: 0 for key in (
        "confirmed_evidence", "partially_supported", "unverified", "no_evidence_found"
    )}
    for item in output_records:
        counts[item["evidence_status"]] += 1

    return {
        "schema_version": "1.0",
        "interpretation_method": "deterministic_evidence_status_classification",
        "source_files": {
            "evidence_match": evidence_data.get("sources", {}).get("resume_file"),
            "matching_score": "ai_engineer_jd_docx_match_score.json",
        },
        "alignment": score_data.get("alignment", {}),
        "summary": {
            "total_requirements": len(output_records),
            **counts,
            "original_matching_score_preserved": True,
        },
        "requirements": output_records,
        "policy": [
            "Evidence status describes the available supporting evidence, not the candidate's actual ability.",
            "Resume-documented and user-confirmed evidence remain distinguishable.",
            "A matched requirement is not an independent skills assessment.",
            "No evidence found must not be interpreted as lack of capability.",
            "Original matching statuses and score values are preserved, not recalculated.",
        ],
    }


def main() -> int:
    try:
        evidence_data = load_json(INPUT_EVIDENCE)
        score_data = load_json(INPUT_SCORE)
        output = build_output(evidence_data, score_data)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)
            file.write("\n")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 2

    print("EVIDENCE STATUS ENGINE COMPLETE")
    print("=" * 48)
    print(f"Requirements          : {output['summary']['total_requirements']}")
    for label in ("confirmed_evidence", "partially_supported", "unverified", "no_evidence_found"):
        print(f"{label.replace('_', ' ').title():22}: {output['summary'][label]}")
    print(f"Alignment score       : {output['alignment'].get('alignment_score')}%")
    print(f"Output                : {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
