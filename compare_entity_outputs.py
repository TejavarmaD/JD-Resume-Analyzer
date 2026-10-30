
import json
import re
import unicodedata
from pathlib import Path


OUTPUT_DIR = Path("structured_results")

PDF_FILE = OUTPUT_DIR / "Tejavarma Dommaraju(Resume)_entities.json"
DOCX_FILE = OUTPUT_DIR / "Tejavarma Dommaraju_Resume_entities.json"

WRAPPED_TEXT_LIST_FIELDS = {"evidence"}
SOURCE_EVIDENCE_FIELDS = {"source_evidence"}
SOURCE_TEXT_FIELDS = {"source_section", "source_section_text"}

# These are reported but do not fail the comparison.
informational_differences = 0

# These indicate a mismatch and cause a non-zero exit code.
substantive_differences = 0

# Record-list fields excluded when comparing section metadata.
SECTION_RECORD_FIELDS = {
    "records",
    "certifications",
    "activities",
}

# Recognized bullet characters at the beginning of a line.
BULLET_PATTERN = re.compile(
    r"^[ \t]*[\u2022\u25cf\u25aa\u25e6\u25a0\u25ab\u2043\u25cb]\s*"
)


def load_json(path: Path) -> dict:
    """Load JSON and ensure its root is an object."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")

    return data


def normalize(value):
    """Normalize whitespace recursively without modifying source data."""
    if isinstance(value, str):
        return " ".join(value.split())

    if isinstance(value, list):
        return [normalize(item) for item in value]

    if isinstance(value, dict):
        return {
            key: normalize(item)
            for key, item in value.items()
        }

    return value


def normalize_wrapped_text(value):
    """Compare wrapped text fragments as one continuous string."""
    if isinstance(value, list):
        return " ".join(
            normalize(item)
            for item in value
            if isinstance(item, str)
        )

    return normalize(value)


def normalize_source_evidence(value):
    """
    Normalize whitespace, line wrapping, and leading bullet markers.

    Words, numbers, punctuation, and headings are preserved.
    """
    if isinstance(value, list):
        parts = value
    elif isinstance(value, str):
        parts = value.splitlines()
    else:
        return normalize(value)

    normalized_parts = []

    for part in parts:
        if not isinstance(part, str):
            normalized_parts.append(str(part))
            continue

        part = unicodedata.normalize("NFC", part)
        part = BULLET_PATTERN.sub("", part)
        part = " ".join(part.split())

        if part:
            normalized_parts.append(part)

    return " ".join(normalized_parts)


def normalize_source_text(value):
    """
    Normalize source sections recursively.

    Formatting differences are ignored, but meaningful content such as
    'Certifications:' and 'Activities:' is retained for comparison.
    """
    if isinstance(value, dict):
        return {
            key: normalize_source_text(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            normalize_source_text(item)
            for item in value
        ]

    if isinstance(value, str):
        return normalize_source_evidence(value)

    return value


def normalize_metadata(metadata):
    """
    Normalize source-text fields inside a metadata dictionary.

    Other fields retain their normal whitespace-only comparison rules.
    Missing keys are not removed.
    """
    if not isinstance(metadata, dict):
        return normalize(metadata)

    normalized = {}

    for key, value in metadata.items():
        if key in SOURCE_TEXT_FIELDS:
            normalized[key] = normalize_source_text(value)
        else:
            normalized[key] = normalize(value)

    return normalized


def classify_source_evidence(pdf_value, docx_value):
    """Classify evidence as exact, formatting-only, or different."""
    if pdf_value == docx_value:
        return "exact"

    if (
        normalize_source_evidence(pdf_value)
        == normalize_source_evidence(docx_value)
    ):
        return "formatting_only"

    return "content_difference"


def report_difference(label, pdf_value, docx_value):
    """Record a substantive mismatch."""
    global substantive_differences

    substantive_differences += 1

    print(f"  SUBSTANTIVE DIFFERENCE: {label}")
    print(f"    PDF : {pdf_value!r}")
    print(f"    DOCX: {docx_value!r}")


def compare_metadata(label, pdf_value, docx_value):
    """Compare metadata after normalizing source-text fields."""
    global informational_differences

    normalized_pdf = normalize_metadata(pdf_value)
    normalized_docx = normalize_metadata(docx_value)

    if normalized_pdf == normalized_docx:
        if pdf_value == docx_value:
            print(f"  MATCH: {label}")
        else:
            informational_differences += 1
            print(f"  FORMATTING-ONLY DIFFERENCE: {label}")
        return

    report_difference(label, normalized_pdf, normalized_docx)


def compare_values(label, pdf_value, docx_value):
    """Compare values using field-specific normalization rules."""
    global informational_differences

    field_name = label.rsplit(".", 1)[-1]

    # Metadata dictionaries need field-aware normalization.
    if (
        field_name == "metadata"
        or label.endswith(" metadata")
        ) and (
            isinstance(pdf_value, dict)
            or isinstance(docx_value, dict)
        ):
        compare_metadata(label, pdf_value, docx_value)
        return

    # Source evidence is retained but compared with formatting tolerance.
    if field_name in SOURCE_EVIDENCE_FIELDS:
        classification = classify_source_evidence(
            pdf_value,
            docx_value,
        )

        if classification == "exact":
            print(f"  EXACT MATCH: {label}")

        elif classification == "formatting_only":
            informational_differences += 1
            print(f"  FORMATTING-ONLY DIFFERENCE: {label}")

        else:
            report_difference(
                label,
                pdf_value,
                docx_value,
            )

        return

    # Original extracted source sections may differ in layout.
    if field_name in SOURCE_TEXT_FIELDS:
        normalized_pdf = normalize_source_text(pdf_value)
        normalized_docx = normalize_source_text(docx_value)

        if normalized_pdf == normalized_docx:
            if pdf_value == docx_value:
                print(f"  EXACT MATCH: {label}")
            else:
                informational_differences += 1
                print(f"  FORMATTING-ONLY DIFFERENCE: {label}")
        else:
            report_difference(
                label,
                normalized_pdf,
                normalized_docx,
            )

        return

    # Evidence lists can contain different line-wrap fragments.
    if field_name in WRAPPED_TEXT_LIST_FIELDS:
        if (
            normalize_wrapped_text(pdf_value)
            == normalize_wrapped_text(docx_value)
        ):
            print(f"  NORMALIZED MATCH: {label}")
        else:
            report_difference(
                label,
                pdf_value,
                docx_value,
            )

        return

    # All other fields use whitespace normalization only.
    if normalize(pdf_value) == normalize(docx_value):
        print(f"  MATCH: {label}")
    else:
        report_difference(
            label,
            pdf_value,
            docx_value,
        )


def compare_record_lists(section_name, pdf_records, docx_records):
    """Compare record collections and every field in each paired record."""
    if (
        not isinstance(pdf_records, list)
        or not isinstance(docx_records, list)
    ):
        report_difference(
            f"{section_name} record collection type",
            type(pdf_records).__name__,
            type(docx_records).__name__,
        )
        return

    if len(pdf_records) != len(docx_records):
        report_difference(
            f"{section_name} record count",
            len(pdf_records),
            len(docx_records),
        )

    for index in range(max(len(pdf_records), len(docx_records))):
        print(f"\n  Record {index + 1}")

        if index >= len(pdf_records):
            report_difference(
                f"{section_name} record {index + 1} missing in PDF",
                None,
                docx_records[index],
            )
            continue

        if index >= len(docx_records):
            report_difference(
                f"{section_name} record {index + 1} missing in DOCX",
                pdf_records[index],
                None,
            )
            continue

        pdf_record = pdf_records[index]
        docx_record = docx_records[index]

        if (
            not isinstance(pdf_record, dict)
            or not isinstance(docx_record, dict)
        ):
            report_difference(
                f"{section_name} record {index + 1} type",
                type(pdf_record).__name__,
                type(docx_record).__name__,
            )
            continue

        keys = sorted(set(pdf_record) | set(docx_record))

        for key in keys:
            label = f"{section_name}[{index}].{key}"

            if key not in pdf_record:
                report_difference(
                    f"{label} missing in PDF",
                    None,
                    docx_record[key],
                )

            elif key not in docx_record:
                report_difference(
                    f"{label} missing in DOCX",
                    pdf_record[key],
                    None,
                )

            else:
                compare_values(
                    label,
                    pdf_record[key],
                    docx_record[key],
                )


def compare_section_metadata(section_name, pdf_section, docx_section):
    """Compare section fields other than record collections."""
    pdf_metadata = {
        key: value
        for key, value in pdf_section.items()
        if key not in SECTION_RECORD_FIELDS
    }

    docx_metadata = {
        key: value
        for key, value in docx_section.items()
        if key not in SECTION_RECORD_FIELDS
    }

    compare_values(
        f"{section_name} metadata",
        pdf_metadata,
        docx_metadata,
    )


def compare_section(label, pdf_data, docx_data, list_key):
    """Validate section presence, compare metadata, then records."""
    print(f"\n[{label.upper()}]")

    if label not in pdf_data or label not in docx_data:
        report_difference(
            f"{label} section presence",
            label in pdf_data,
            label in docx_data,
        )
        return

    pdf_section = pdf_data[label]
    docx_section = docx_data[label]

    if (
        not isinstance(pdf_section, dict)
        or not isinstance(docx_section, dict)
    ):
        report_difference(
            f"{label} section type",
            type(pdf_section).__name__,
            type(docx_section).__name__,
        )
        return

    compare_section_metadata(
        label,
        pdf_section,
        docx_section,
    )

    if list_key not in pdf_section or list_key not in docx_section:
        report_difference(
            f"{label}.{list_key} key presence",
            list_key in pdf_section,
            list_key in docx_section,
        )
        return

    compare_record_lists(
        label,
        pdf_section[list_key],
        docx_section[list_key],
    )


def compare_top_level_metadata(pdf_data, docx_data):
    """Compare top-level metadata without comparing sections twice."""
    print("\n[TOP-LEVEL METADATA]")

    ignored_fields = {
        "source_file",
        "contact",
        "work_experience",
        "projects",
        "skills",
        "education",
        "certifications_and_activities",
    }

    keys = (
        set(pdf_data) | set(docx_data)
    ) - ignored_fields

    for key in sorted(keys):
        if key not in pdf_data:
            report_difference(
                f"top-level key '{key}' missing in PDF",
                None,
                docx_data[key],
            )

        elif key not in docx_data:
            report_difference(
                f"top-level key '{key}' missing in DOCX",
                pdf_data[key],
                None,
            )

        else:
            compare_values(
                key,
                pdf_data[key],
                docx_data[key],
            )


def compare_contact(pdf_data, docx_data):
    """Compare contact information."""
    print("\n[CONTACT]")

    if "contact" not in pdf_data or "contact" not in docx_data:
        report_difference(
            "contact key presence",
            "contact" in pdf_data,
            "contact" in docx_data,
        )
        return

    compare_values(
        "contact",
        pdf_data["contact"],
        docx_data["contact"],
    )


def compare_activities(pdf_data, docx_data):
    """Compare activities stored inside certifications_and_activities."""
    print("\n[ACTIVITIES]")

    pdf_ca = pdf_data.get("certifications_and_activities")
    docx_ca = docx_data.get("certifications_and_activities")

    if not isinstance(pdf_ca, dict) or not isinstance(docx_ca, dict):
        report_difference(
            "certifications_and_activities section type for activities",
            type(pdf_ca).__name__,
            type(docx_ca).__name__,
        )
        return

    if "activities" not in pdf_ca or "activities" not in docx_ca:
        report_difference(
            "certifications_and_activities.activities key presence",
            "activities" in pdf_ca,
            "activities" in docx_ca,
        )
        return

    compare_record_lists(
        "ACTIVITIES",
        pdf_ca["activities"],
        docx_ca["activities"],
    )


def compare_review_warnings(pdf_data, docx_data):
    """Compare review warnings."""
    print("\n[REVIEW WARNINGS]")

    if "review_warnings" not in pdf_data or "review_warnings" not in docx_data:
        report_difference(
            "review_warnings key presence",
            "review_warnings" in pdf_data,
            "review_warnings" in docx_data,
        )
        return

    compare_values(
        "review_warnings",
        pdf_data["review_warnings"],
        docx_data["review_warnings"],
    )


def main():
    global substantive_differences, informational_differences

    # Reset counters so repeated calls do not accumulate old results.
    substantive_differences = 0
    informational_differences = 0

    try:
        for path in (PDF_FILE, DOCX_FILE):
            if not path.is_file():
                raise FileNotFoundError(
                    f"Required JSON file not found: {path}"
                )

        pdf_data = load_json(PDF_FILE)
        docx_data = load_json(DOCX_FILE)

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 2

    print("CROSS-FORMAT ENTITY COMPARISON")
    print("=" * 60)
    print(f"PDF : {PDF_FILE.name}")
    print(f"DOCX: {DOCX_FILE.name}")

    compare_top_level_metadata(pdf_data, docx_data)
    compare_contact(pdf_data, docx_data)

    for section in (
        "work_experience",
        "projects",
        "skills",
        "education",
    ):
        compare_section(
            section,
            pdf_data,
            docx_data,
            "records",
        )

    compare_section(
        "certifications_and_activities",
        pdf_data,
        docx_data,
        "certifications",
    )

    compare_activities(pdf_data, docx_data)
    compare_review_warnings(pdf_data, docx_data)

    print("\n" + "=" * 60)
    print(
        f"Formatting-only differences: {informational_differences}"
    )
    print(f"Substantive differences: {substantive_differences}")

    if substantive_differences:
        print("RESULT: FAIL — investigate the discrepancies.")
        return 1

    print(
        "RESULT: PASS — compared fields match after permitted normalization."
    )
    print("Note: A passing comparison does not prove factual accuracy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
