
import json
import re
from pathlib import Path

from skill_tag_dictionary import DICTIONARY_VERSION, SKILL_DICTIONARY


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "jd_results" / "ai_engineer_jd_analysis.json"
OUTPUT_FILE = BASE_DIR / "jd_results" / "ai_engineer_jd_skill_tags.json"

CATEGORIES = (
    "concepts",
    "technologies",
    "platforms",
    "standards",
)

TECHNICAL_SIGNALS = {
    "api", "apis", "authentication", "authorization",
    "validation", "database", "databases", "latency",
    "token", "tokens", "consumption", "indexing",
    "monitoring", "logging", "tracing", "reranking",
    "deployment", "integration", "integrations",
    "platform", "platforms", "enterprise",
    "inference", "fine-tuning", "fine tuning",
    "vector", "vectors", "pipeline", "pipelines",
    "security", "encryption", "access control",
    "error handling", "input validation",
    "third-party", "microservices", "multimodal",
}



def compile_dictionary():
    """Compile the flat skill dictionary into searchable regex patterns."""
    compiled = []

    for canonical_id, details in SKILL_DICTIONARY.items():
        category = details["category"]
        display_name = details["display_name"]

        aliases = set(details.get("aliases", []))
        aliases.add(display_name)
        aliases.add(canonical_id.replace("_", " "))

        for alias in aliases:
            alias = alias.strip()

            if not alias:
                continue

            pattern = re.compile(
                r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                re.IGNORECASE,
            )

            compiled.append({
                "category": category,
                "tag": canonical_id,
                "display_name": display_name,
                "alias": alias,
                "pattern": pattern,
            })

    compiled.sort(
        key=lambda item: len(item["alias"]),
        reverse=True,
    )

    return compiled



def find_matches(requirement_text, compiled_dictionary):
    """Find explicit dictionary matches, preferring longer aliases."""
    candidates = []

    for entry in compiled_dictionary:
        for match in entry["pattern"].finditer(requirement_text):
            candidates.append({
                "category": entry["category"],
                "tag": entry["tag"],
                "display_name": entry["display_name"],
                "matched_text": match.group(),
                "start": match.start(),
                "end": match.end(),
            })

    candidates.sort(
        key=lambda item: (
            -(item["end"] - item["start"]),
            item["start"],
        )
    )

    selected = []

    for candidate in candidates:
        overlaps = any(
            candidate["start"] < existing["end"]
            and candidate["end"] > existing["start"]
            for existing in selected
        )

        if not overlaps:
            selected.append(candidate)

    selected.sort(key=lambda item: item["start"])

    return selected


def find_unmatched_terms(requirement_text, matches):
    """Find plausible technical terms not covered by dictionary matches."""
    covered = [
        (match["start"], match["end"])
        for match in matches
    ]

    candidates = []

    # Detect uppercase acronyms and mixed-case technical names.
    candidate_patterns = [
        re.compile(
            r"\b(?:[A-Z][A-Z0-9]*(?:/[A-Z0-9]+)*|"
            r"[a-z]+[A-Z][A-Za-z0-9]*)\b"
        ),
        re.compile(r"\b[A-Za-z]+(?:-[A-Za-z]+)+\b"),
    ]

    for pattern in candidate_patterns:
        for match in pattern.finditer(requirement_text):
            candidates.append(match)

    # Detect terms containing known technical signals.
    for signal in sorted(TECHNICAL_SIGNALS, key=len, reverse=True):
        pattern = re.compile(
            r"(?<!\w)" + re.escape(signal) + r"(?!\w)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(requirement_text):
            candidates.append(match)

    results = []
    seen = set()

    for candidate in sorted(
        candidates,
        key=lambda item: item.start(),
    ):
        start, end = candidate.span()

        if any(
            start < covered_end and end > covered_start
            for covered_start, covered_end in covered
        ):
            continue

        matched_text = requirement_text[start:end]
        key = (start, end)

        if key in seen:
            continue

        seen.add(key)

        results.append({
            "term": matched_text,
            "evidence": {
                "start": start,
                "end": end,
                "matched_text": matched_text,
            },
            "review_status": "needs_manual_review",
        })

    return results


def build_skill_tags(matches, requirement_text):
    """Group matched tags by category and preserve evidence."""
    result = {
        category: []
        for category in CATEGORIES
    }

    grouped = {}

    for match in matches:
        key = (match["category"], match["tag"])

        if key not in grouped:
            grouped[key] = {
                "tag": match["tag"],
                "display_name": match["display_name"],
                "matched_text": match["matched_text"],
                "extraction_type": "explicit",
                "evidence": [],
            }

        grouped[key]["evidence"].append({
            "start": match["start"],
            "end": match["end"],
            "matched_text": match["matched_text"],
        })

    for (category, _), tag_data in grouped.items():
        result[category].append(tag_data)

    return result


def extract_alternatives(requirement_text, matches):
    """Identify explicitly stated OR alternatives."""
    alternatives = []
    alternative_count = 0

    for index in range(len(matches) - 1):
        first = matches[index]
        second = matches[index + 1]

        between = requirement_text[
            first["end"]:second["start"]
        ]

        if re.search(r"\bor\b", between, re.IGNORECASE):
            alternative_count += 1

            alternatives.append({
                "group_id": f"ALT-{alternative_count:03d}",
                "operator": "OR",
                "tags": [
                    first["tag"],
                    second["tag"],
                ],
                "source_text": requirement_text[
                    first["start"]:second["end"]
                ],
                "evidence": {
                    "start": first["start"],
                    "end": second["end"],
                },
            })

    return alternatives


def build_requirement_output(record, compiled_dictionary):
    """Build the structured output for one JD requirement."""
    requirement_text = record.get("requirement", "")

    if not isinstance(requirement_text, str) or not requirement_text.strip():
        raise ValueError(
            f"Requirement {record.get('id', 'UNKNOWN')} has no valid text."
        )

    matches = find_matches(
        requirement_text,
        compiled_dictionary,
    )

    unmatched_terms = find_unmatched_terms(
        requirement_text,
        matches,
    )

    return {
        "requirement_id": record.get("id", "UNKNOWN"),
        "requirement_text": requirement_text,
        "skill_tags": build_skill_tags(
            matches,
            requirement_text,
        ),
        "alternatives": extract_alternatives(
            requirement_text,
            matches,
        ),
        "unmatched_terms": unmatched_terms,
    }


def build_summary(requirements):
    """Calculate output summary statistics."""
    total_requirements = len(requirements)

    requirements_with_tags = 0
    total_tag_occurrences = 0
    unique_tags = set()

    unmatched_term_count = sum(
        len(requirement.get("unmatched_terms", []))
        for requirement in requirements
    )

    for requirement in requirements:
        has_tags = False

        for category in CATEGORIES:
            for tag in requirement["skill_tags"][category]:
                has_tags = True
                unique_tags.add(tag["tag"])
                total_tag_occurrences += len(tag["evidence"])

        if has_tags:
            requirements_with_tags += 1

    return {
        "total_requirements": total_requirements,
        "requirements_with_tags": requirements_with_tags,
        "requirements_without_tags": (
            total_requirements - requirements_with_tags
        ),
        "total_tag_occurrences": total_tag_occurrences,
        "total_unique_tags": len(unique_tags),
        "unmatched_term_count": unmatched_term_count,
    }


def main():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Input analysis file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        analysis_data = json.load(file)

    source_requirements = analysis_data.get("requirements", [])

    if not isinstance(source_requirements, list):
        raise ValueError(
            "The requirements field must contain a list."
        )

    compiled_dictionary = compile_dictionary()

    requirements = [
        build_requirement_output(record, compiled_dictionary)
        for record in source_requirements
    ]

    output_data = {
        "schema_version": "1.0",
        "tagging_method": "deterministic_rule_based",
        "dictionary_version": DICTIONARY_VERSION,
        "source": {
            "jd_file": "ai_engineer_jd.txt",
            "analysis_file": INPUT_FILE.name,
        },
        "summary": build_summary(requirements),
        "requirements": requirements,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    summary = output_data["summary"]

    print("SKILL TAG EXTRACTION COMPLETE")
    print("=" * 45)
    print(f"Total requirements     : {summary['total_requirements']}")
    print(f"Tagged requirements    : {summary['requirements_with_tags']}")
    print(f"Untagged requirements  : {summary['requirements_without_tags']}")
    print(f"Tag occurrences        : {summary['total_tag_occurrences']}")
    print(f"Unique tags used       : {summary['total_unique_tags']}")
    print(f"Unmatched terms        : {summary['unmatched_term_count']}")
    print(f"Dictionary version     : {DICTIONARY_VERSION}")
    print(f"Output                 : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
