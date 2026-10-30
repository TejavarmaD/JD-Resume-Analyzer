
import json
from pathlib import Path

OUTPUT_DIR = Path("structured_results")

FILES = [
    OUTPUT_DIR / "Tejavarma Dommaraju(Resume)_entities.json",
    OUTPUT_DIR / "Tejavarma Dommaraju_Resume_entities.json",
]

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "source_file",
    "contact",
    "work_experience",
    "projects",
    "skills",
    "education",
    "certifications_and_activities",
    "source_section_text",
    "parser_validation",
    "review_warnings",
}


def audit_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    errors = []
    warnings = []

    missing_keys = EXPECTED_TOP_LEVEL_KEYS - data.keys()
    if missing_keys:
        errors.append(f"Missing top-level keys: {sorted(missing_keys)}")

    if data.get("schema_version") != "1.1":
        warnings.append(
            f"Unexpected schema version: {data.get('schema_version')}"
        )

    if not isinstance(data.get("contact"), dict):
        errors.append("'contact' must be an object")

    collection_specs = {
        "work_experience": ("records", dict),
        "projects": ("records", dict),
        "skills": ("records", dict),
        "education": ("records", dict),
        "certifications_and_activities": ("certifications", dict),
    }

    for section, (field, record_type) in collection_specs.items():
        section_data = data.get(section)

        if not isinstance(section_data, dict):
            errors.append(f"'{section}' must be an object")
            continue

        records = section_data.get(field)

        if not isinstance(records, list):
            errors.append(f"'{section}.{field}' must be a list")
            continue

        for index, record in enumerate(records):
            if not isinstance(record, record_type):
                errors.append(
                    f"'{section}.{field}[{index}]' must be an object"
                )
                continue

            if section == "work_experience":
                required = {
                    "employer",
                    "job_title",
                    "responsibilities",
                    "source_evidence",
                    "needs_review",
                    "review_reasons",
                }
            elif section == "projects":
                required = {
                    "name",
                    "evidence",
                    "source_evidence",
                    "needs_review",
                    "review_reasons",
                }
            elif section == "skills":
                required = {
                    "category",
                    "items",
                    "source_evidence",
                    "needs_review",
                    "review_reasons",
                }
            elif section == "education":
                required = {
                    "text",
                    "source_evidence",
                    "record_type",
                    "needs_review",
                    "review_reasons",
                }
            else:
                required = {
                    "name",
                    "source_evidence",
                    "needs_review",
                    "review_reasons",
                }

            missing = required - record.keys()
            if missing:
                errors.append(
                    f"{section}.{field}[{index}] missing: {sorted(missing)}"
                )

            if "needs_review" in record:
                if not isinstance(record["needs_review"], bool):
                    errors.append(
                        f"{section}.{field}[{index}].needs_review "
                        "must be boolean"
                    )

            if "review_reasons" in record:
                if not isinstance(record["review_reasons"], list):
                    errors.append(
                        f"{section}.{field}[{index}].review_reasons "
                        "must be a list"
                    )
                elif (
                    record.get("needs_review") is False
                    and record["review_reasons"]
                ):
                    warnings.append(
                        f"{section}.{field}[{index}] has review reasons "
                        "but needs_review is false"
                    )

    return {
        "file": path.name,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    failed = False

    for path in FILES:
        if not path.exists():
            print(f"\nMISSING FILE: {path}")
            failed = True
            continue

        result = audit_file(path)

        print(f"\n--- {result['file']} ---")

        if result["errors"]:
            failed = True
            for error in result["errors"]:
                print(f"ERROR: {error}")
        else:
            print("Structural checks: PASS")

        for warning in result["warnings"]:
            print(f"WARNING: {warning}")

    print("\nOVERALL:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
