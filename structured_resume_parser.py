
from pathlib import Path
import json
import re
import sys

from extract_documents import extract_docx, extract_pdf


SECTION_ALIASES = {
    "EXECUTIVE SUMMARY": {
        "executive summary", "professional summary", "summary",
        "profile", "professional profile", "career summary",
    },
    "WORK EXPERIENCE": {
        "work experience", "professional experience",
        "employment history", "work history", "experience",
    },
    "PROJECT WORK": {
        "project work", "projects", "personal projects",
        "academic projects", "key projects",
    },
    "SKILLS": {
        "skills", "technical skills", "core skills",
        "skills and competencies", "technical competencies",
    },
    "EDUCATION": {
        "education", "educational qualifications",
        "academic background", "academic qualifications",
    },
    "CERTIFICATIONS & ACHIEVEMENTS": {
        "certifications & achievements",
        "certifications and achievements",
        "certifications", "certificates",
        "certifications & activities", "achievements",
    },
}

EXPECTED_ORDER = list(SECTION_ALIASES.keys())


def normalize_heading(line: str) -> str:
    line = line.strip().casefold()
    line = re.sub(r"[\s:|]+$", "", line)
    return re.sub(r"\s+", " ", line)


def detect_heading(line: str) -> str | None:
    normalized = normalize_heading(line)

    for canonical_name, aliases in SECTION_ALIASES.items():
        normalized_aliases = {
            normalize_heading(alias) for alias in aliases
        }
        if normalized in normalized_aliases:
            return canonical_name

    return None


def extract_text(file_path: Path) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    suffix = file_path.suffix.casefold()

    if suffix == ".docx":
        return extract_docx(file_path)

    if suffix == ".pdf":
        text, _, _ = extract_pdf(file_path)
        return text

    raise ValueError("Supported formats are PDF and DOCX.")


def normalize_for_analysis(original_text: str) -> str:
    """
    Create a separate analysis-friendly representation.

    Does not modify original_text or remove words.
    Removes common bullet symbols and normalizes whitespace.
    """
    normalized = re.sub(
        r"(?m)^\s*[•▪◦‣]\s*",
        "",
        original_text,
    )

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_contact(preliminary_lines: list[str]) -> dict:
    """
    Extract identifiable contact fields from pre-section text.
    Unidentified fields remain None; do not guess.
    """
    preamble_text = "\n".join(preliminary_lines)

    email_match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        preamble_text,
        re.IGNORECASE,
    )

    phone_match = re.search(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        preamble_text,
    )

    github_match = re.search(
        r"https?://(?:www\.)?github\.com/[^\s|]+",
        preamble_text,
        re.IGNORECASE,
    )

    linkedin_match = re.search(
        r"https?://(?:www\.)?linkedin\.com/[^\s|]+",
        preamble_text,
        re.IGNORECASE,
    )

    name = None
    for line in preliminary_lines:
        candidate = line.strip()
        if (
            candidate
            and "@" not in candidate
            and not re.search(r"https?://", candidate, re.I)
            and not re.search(r"\d{5,}", candidate)
        ):
            name = candidate
            break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "linkedin_url": (
            linkedin_match.group(0) if linkedin_match else None
        ),
        "github_url": github_match.group(0) if github_match else None,
        "source_text": preamble_text,
    }


def identify_warnings(
    original_text: str,
    sections: dict,
    contact: dict,
) -> list[dict]:
    warnings = []

    # Preserve uncertainty rather than turning it into a confirmed claim.
    uncertain_patterns = [
        r"\bif accurate\b",
        r"\bpossibly\b",
        r"\bnot verified\b",
        r"\bto be confirmed\b",
    ]

    for pattern in uncertain_patterns:
        for match in re.finditer(
            pattern, original_text, re.IGNORECASE
        ):
            start = max(0, match.start() - 70)
            end = min(len(original_text), match.end() + 70)

            warnings.append({
                "type": "uncertain_claim",
                "severity": "review",
                "message": (
                    "Potentially uncertain wording found. "
                    "Verify before treating it as a confirmed qualification."
                ),
                "matched_text": match.group(0),
                "context": original_text[start:end],
                "auto_corrected": False,
            })

    # Example: the inspected PDF ended with "rates.n".
    # Flag the pattern; do not remove the character automatically.
    if re.search(r"\.\s*n\s*$", original_text, re.IGNORECASE):
        warnings.append({
            "type": "possible_extraction_artifact",
            "severity": "review",
            "message": (
                "Text ends with '.n'. Inspect the source document "
                "to determine whether this is a genuine character "
                "or an extraction artifact."
            ),
            "matched_text": original_text[-80:],
            "auto_corrected": False,
        })

    if "\ufffd" in original_text:
        warnings.append({
            "type": "encoding_issue",
            "severity": "review",
            "message": (
                "Replacement character detected. Check the source "
                "document for text that may not have extracted correctly."
            ),
            "matched_text": "\ufffd",
            "auto_corrected": False,
        })

    # Missing contact fields are reported, not inferred.
    for field in ("email", "phone"):
        if not contact[field]:
            warnings.append({
                "type": "missing_contact_field",
                "severity": "information",
                "message": f"No {field} could be identified in the extracted preamble.",
                "field": field,
                "auto_corrected": False,
            })

    # Preserve a human review reminder for the specific skills statement.
    skills_text = sections.get("SKILLS", {}).get("original_text", "")
    if re.search(r"\bif accurate\b", skills_text, re.IGNORECASE):
        warnings.append({
            "type": "qualification_requires_confirmation",
            "severity": "review",
            "message": (
                "The sustainability-framework statement includes "
                "'if accurate'. Confirm the claim with the candidate "
                "before using it as verified evidence."
            ),
            "auto_corrected": False,
        })

    return warnings


def parse_resume(text: str) -> dict:
    section_lines = {name: [] for name in EXPECTED_ORDER}
    preamble = []
    detected_order = []
    current_section = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        heading = detect_heading(line)

        # Preserve subsection headings inside the certifications section.
        if (
            current_section == "CERTIFICATIONS & ACHIEVEMENTS"
            and normalize_heading(line) == "certifications"
        ):
            section_lines[current_section].append(line)
            continue
        if heading:
            current_section = heading

            if heading not in detected_order:
                detected_order.append(heading)

            continue

        if current_section is None:
            preamble.append(line)
        else:
            section_lines[current_section].append(raw_line.strip())

    contact = extract_contact(preamble)

    sections = {}

    for name in EXPECTED_ORDER:
        if name not in detected_order:
            continue

        original_section_text = "\n".join(section_lines[name])

        sections[name] = {
            # Evidence as extracted. Do not normalize this field.
            "original_text": original_section_text,

            # Separate representation for search/matching.
            "normalized_text": normalize_for_analysis(
                original_section_text
            ),

            "line_count": len(section_lines[name]),
            "character_count": len(original_section_text),
            "is_empty": not bool(original_section_text.strip()),
        }

    missing_sections = [
        name for name in EXPECTED_ORDER
        if name not in detected_order
    ]

    empty_sections = [
        name for name in detected_order
        if not section_lines[name]
    ]

    detected_positions = [
        EXPECTED_ORDER.index(name) for name in detected_order
    ]

    order_is_valid = (
        detected_positions == sorted(detected_positions)
    )

    warnings = identify_warnings(text, sections, contact)

    return {
        "schema_version": "2.0",
        "source": {
            "extracted_character_count": len(text),
            "original_extracted_text": text,
        },
        "contact": contact,
        "sections": sections,
        "unclassified_content": {
            "PREAMBLE": preamble,
        },
        "validation": {
            "detected_sections": detected_order,
            "missing_expected_sections": missing_sections,
            "empty_detected_sections": empty_sections,
            "section_order_valid": order_is_valid,
            "nonempty_section_count": sum(
                not item["is_empty"]
                for item in sections.values()
            ),
            "warning_count": len(warnings),
            "has_review_warnings": bool(warnings),
        },
        "review_warnings": warnings,
    }


def main() -> None:
    if len(sys.argv) != 2:
        print(
            'Usage: python structured_resume_parser.py '
            '"path\\to\\resume.pdf"'
        )
        raise SystemExit(1)

    file_path = Path(sys.argv[1])

    try:
        text = extract_text(file_path)

        if not text.strip():
            print("ERROR: No readable text was extracted.")
            raise SystemExit(1)

        result = parse_resume(text)

        output_dir = Path("structured_results")
        output_dir.mkdir(exist_ok=True)

        output_file = (
            output_dir / f"{file_path.stem}_structured.json"
        )

        output_file.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        validation = result["validation"]

        print(f"\nInput file: {file_path.name}")
        print(
            "Extracted characters: "
            f"{result['source']['extracted_character_count']}"
        )
        
        print(
            "Detected sections: "
            f"{validation['nonempty_section_count']}"
        )
        print(
            "Section order valid: "
            f"{validation['section_order_valid']}"
        )

        print("\nContact extraction:")
        for field in (
            "name", "email", "phone", "linkedin_url", "github_url"
        ):
            print(f"  {field}: {result['contact'][field]}")

        print("\nSection summary:")
        for name, details in result["sections"].items():
            print(
                f"  {name}: {details['line_count']} lines, "
                f"{details['character_count']} original characters"
            )

        print("\nReview warnings:")
        if not result["review_warnings"]:
            print("  None detected")
        else:
            for warning in result["review_warnings"]:
                print(
                    f"  [{warning['severity']}] "
                    f"{warning['type']}: {warning['message']}"
                )

        print(f"\nJSON saved to:\n{output_file.resolve()}")

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
