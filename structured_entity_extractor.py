
from pathlib import Path
import json
import re
import sys

from structured_resume_parser import extract_text, parse_resume


OUTPUT_DIR = Path("structured_results")


def clean_display_text(text: str) -> str:
    """Normalize whitespace without changing original source evidence."""
    return re.sub(r"\s+", " ", text).strip()


def remove_bullet(text: str) -> str:
    """Remove a leading bullet for display purposes."""
    return re.sub(r"^\s*[•▪◦‣*\-]\s*", "", text).strip()


def split_pdf_wrapped_text(text: str) -> list[str]:
    """Rejoin visual line wraps while preserving likely headings and bullets."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraphs = []
    current = ""

    def looks_like_heading(line: str) -> bool:
        cleaned = remove_bullet(line)
        return bool(
            cleaned.isupper()
            or re.match(r"^[A-Z][^.!?]{0,100}:\s*$", cleaned)
            or re.match(
                r"^(Data Forge|Revenue Insights|Activities|Achievements|"
                r"Certifications)\b",
                cleaned,
                re.IGNORECASE,
            )
            or re.match(
                r"^(Omnicom Global Solutions|Johnson Controls),\s*",
                cleaned,
                re.IGNORECASE,
            )
        )

    for line in lines:
        if re.match(r"^[•▪◦‣]\s*", line):
            if current:
                paragraphs.append(current)
            current = remove_bullet(line)
            continue

        if current and looks_like_heading(line):
            paragraphs.append(current)
            current = remove_bullet(line)
            continue

        if current:
            current += " " + line
        else:
            current = remove_bullet(line)

    if current:
        paragraphs.append(current)

    return paragraphs


def extract_work_experience(section: dict) -> dict:
    """Extract work experience while joining wrapped responsibility lines."""
    text = section["original_text"]
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    header_pattern = re.compile(
        r"^(?P<employer>Omnicom Global Solutions|Johnson Controls),\s*"
        r"(?P<location>[A-Za-z .-]+?)\s+"
        r"(?P<dates>(?:Dec(?:ember)?\s+2024\s*[–-]\s*Present)|"
        r"(?:Jan(?:uary)?\s+2024\s*-\s*June\s+2024))$",
        re.IGNORECASE,
    )

    bullet_pattern = re.compile(r"^\s*[•●▪◦‣*\-]\s*")
    sentence_end_pattern = re.compile(r"""[.!?]["')\]]*$""")

    records = []
    current = None

    for line in lines:
        normalized = clean_display_text(line)
        match = header_pattern.match(normalized)

        if match:
            if current:
                records.append(current)

            current = {
                "employer": match.group("employer"),
                "location": clean_display_text(match.group("location")),
                "dates": clean_display_text(match.group("dates")),
                "job_title": None,
                "responsibilities": [],
                "source_evidence": [line],
                "needs_review": False,
                "review_reasons": [],
            }
            continue

        if current is None:
            continue

        current["source_evidence"].append(line)
        has_bullet = bool(bullet_pattern.match(line))
        cleaned_line = clean_display_text(remove_bullet(line))

        if not cleaned_line:
            continue

        if current["job_title"] is None:
            current["job_title"] = cleaned_line
            continue

        responsibilities = current["responsibilities"]

        if not responsibilities or has_bullet:
            responsibilities.append(cleaned_line)
        elif sentence_end_pattern.search(responsibilities[-1]):
            responsibilities.append(cleaned_line)
        else:
            responsibilities[-1] = clean_display_text(
                f"{responsibilities[-1]} {cleaned_line}"
            )

    if current:
        records.append(current)

    for record in records:
        if not record["job_title"]:
            record["needs_review"] = True
            record["review_reasons"].append(
                "Job title could not be identified confidently."
            )

        if not record["responsibilities"]:
            record["needs_review"] = True
            record["review_reasons"].append(
                "No responsibilities were identified."
            )

    return {
        "records": records,
        "status": "extracted" if records else "needs_review",
        "review_reasons": [] if records else [
            "No employer/date records matched the current explicit rules."
        ],
        "source_section": text,
    }


def extract_projects(section: dict) -> dict:
    """Extract projects from headings while preserving source evidence."""
    text = section["original_text"]

    project_heading_patterns = [
        re.compile(
            r"Data Forge:\s*AI-Powered Contract ETL\s*&\s*"
            r"Risk Intelligence Platform:?",
            re.IGNORECASE,
        ),
        re.compile(
            r"Revenue Insights\s*\(Hospitality Domain\)\s*[–-]\s*"
            r"AtliQ Grands:?",
            re.IGNORECASE,
        ),
    ]

    records = []
    current = None

    for line in text.splitlines():
        cleaned = clean_display_text(remove_bullet(line))

        if not cleaned:
            continue

        matched_pattern = next(
            (
                pattern
                for pattern in project_heading_patterns
                if pattern.search(cleaned)
            ),
            None,
        )

        if matched_pattern:
            if current:
                records.append(current)

            heading_match = matched_pattern.search(cleaned)
            heading = clean_display_text(
                heading_match.group(0)
            ).rstrip(":")

            current = {
                "name": heading,
                "evidence": [],
                "source_evidence": [line],
                "needs_review": False,
                "review_reasons": [],
            }

            remainder = (
                cleaned[:heading_match.start()]
                + " "
                + cleaned[heading_match.end():]
            ).strip().lstrip(":").strip()

            if remainder:
                current["evidence"].append(remainder)

            continue

        if current is not None:
            current["source_evidence"].append(line)
            current["evidence"].append(cleaned)

    if current:
        records.append(current)

    if not records:
        return {
            "records": [],
            "status": "needs_review",
            "review_reasons": [
                "No project headings matched the configured patterns."
            ],
            "source_section": text,
        }

    for record in records:
        if not record["evidence"]:
            record["needs_review"] = True
            record["review_reasons"].append(
                "No project evidence was extracted."
            )

        if any(
            re.search(r"\.n\s*$", item, re.IGNORECASE)
            for item in record["evidence"]
        ):
            record["needs_review"] = True
            reason = (
                "Possible PDF extraction artifact: evidence ends with "
                "'.n'. Verify against the original document."
            )
            if reason not in record["review_reasons"]:
                record["review_reasons"].append(reason)

    return {
        "records": records,
        "status": "extracted",
        "source_section": text,
    }


def split_top_level_commas(text: str) -> list[str]:
    """Split commas only when they are outside parentheses."""
    items = []
    current = []
    depth = 0

    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)

        if char == "," and depth == 0:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
        else:
            current.append(char)

    final_item = "".join(current).strip()
    if final_item:
        items.append(final_item)

    return items


def extract_skills(section: dict) -> dict:
    """Extract skill categories and preserve their original source evidence."""
    text = section["original_text"]
    records = []
    unparsed_lines = []
    logical_records = []
    current_category = None
    current_raw_items = []
    current_source_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if ":" in line:
            if current_category is not None:
                logical_records.append({
                    "category": current_category,
                    "raw_items": " ".join(current_raw_items),
                    "source_evidence": "\n".join(current_source_lines),
                })

            category, raw_items = line.split(":", 1)
            current_category = clean_display_text(category)
            current_raw_items = [raw_items.strip()]
            current_source_lines = [line]

        elif current_category is not None:
            current_raw_items.append(line)
            current_source_lines.append(line)

        else:
            unparsed_lines.append(line)

    if current_category is not None:
        logical_records.append({
            "category": current_category,
            "raw_items": " ".join(current_raw_items),
            "source_evidence": "\n".join(current_source_lines),
        })

    for record in logical_records:
        raw_items = record["raw_items"]
        items = [
            clean_display_text(item)
            for item in split_top_level_commas(raw_items)
            if clean_display_text(item)
        ]

        # Do not expose drafting notes as extracted skills.
        items = [
            item
            for item in items
            if not re.search(r"\bif accurate\b", item, re.IGNORECASE)
        ]

        review_reasons = []

        if re.search(r"\bif accurate\b", raw_items, re.IGNORECASE):
            review_reasons.append(
                "Contains wording requiring confirmation."
            )

        if (
            len(record["source_evidence"].splitlines()) > 1
            and not split_top_level_commas(raw_items)
        ):
            review_reasons.append(
                "Multiple source lines were joined and skill boundaries "
                "could not be confidently identified."
            )

        if not items:
            review_reasons.append("No skill items were extracted.")

        records.append({
            "category": record["category"],
            "items": items,
            "source_evidence": record["source_evidence"],
            "needs_review": bool(review_reasons),
            "review_reasons": review_reasons,
        })

    return {
        "records": records,
        "unparsed_lines": unparsed_lines,
        "source_section": text,
    }


def extract_education(section: dict) -> dict:
    """Extract education fields while preserving each original source line."""
    text = section["original_text"]
    raw_lines = [line for line in text.splitlines() if line.strip()]
    lines = [clean_display_text(line) for line in raw_lines]
    records = []

    date_pattern = re.compile(
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\s*[-–]\s*"
        r"(Present|January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\b",
        re.IGNORECASE,
    )

    for raw_line, line in zip(raw_lines, lines):
        record = {
            "text": line,
            "source_evidence": raw_line,
            "record_type": "unclassified",
            "institution": None,
            "school": None,
            "location": None,
            "dates": None,
            "degree": None,
            "field_of_study": None,
            "grade": None,
            "honors": None,
            "needs_review": False,
            "review_reasons": [],
        }

        if "Jain University" in line:
            parts = [part.strip() for part in line.split("|")]
            record["record_type"] = "institution"
            record["institution"] = parts[0] if parts else None
            record["school"] = parts[1] if len(parts) > 1 else None

            if len(parts) > 2:
                location_and_dates = parts[2]
                date_match = date_pattern.search(location_and_dates)

                if date_match:
                    record["dates"] = clean_display_text(date_match.group(0))
                    record["location"] = clean_display_text(
                        location_and_dates[:date_match.start()]
                    ).strip(" ,|-")
                else:
                    record["location"] = location_and_dates or None

            required = {
                "institution": record["institution"],
                "school": record["school"],
                "location": record["location"],
                "dates": record["dates"],
            }

            missing = [
                field for field, value in required.items() if not value
            ]

            if missing:
                record["needs_review"] = True
                record["review_reasons"].append(
                    "Could not confidently extract: "
                    + ", ".join(missing)
                    + "."
                )

        elif re.search(r"\bBachelor of Technology\b", line, re.I):
            record["record_type"] = "degree"
            degree_match = re.search(
                r"\bBachelor of Technology\b", line, re.I
            )
            record["degree"] = degree_match.group(0) if degree_match else None

            grade_match = re.search(
                r"\b(?:CGPA|GPA)\s*:\s*"
                r"(\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?)",
                line,
                re.I,
            )

            if grade_match:
                record["grade"] = re.sub(r"\s+", "", grade_match.group(1))

            field_match = re.search(
                r"\bCSE\b(?:\s*\(majoring in [^)]+\))?",
                line,
                re.I,
            )

            if field_match:
                record["field_of_study"] = field_match.group(0)

            if not record["field_of_study"] or not record["grade"]:
                record["needs_review"] = True
                record["review_reasons"].append(
                    "Field of study or grade could not be "
                    "extracted confidently."
                )

        elif re.search(r"\bHonors?\b|\bHonours?\b", line, re.I):
            record["record_type"] = "honors"
            record["honors"] = line

        else:
            record["needs_review"] = True
            record["review_reasons"].append(
                "Education line could not be classified confidently."
            )

        records.append(record)

    degree_records = [
        record for record in records if record["record_type"] == "degree"
    ]
    honors_records = [
        record for record in records if record["record_type"] == "honors"
    ]

    if len(degree_records) == 1 and len(honors_records) == 1:
        degree_records[0]["honors"] = honors_records[0]["honors"]
    elif degree_records or honors_records:
        for record in degree_records:
            record["needs_review"] = True
            reason = "Degree-to-honors association requires verification."
            if reason not in record["review_reasons"]:
                record["review_reasons"].append(reason)

    return {
        "records": records,
        "source_section": text,
    }


def is_certification_continuation(text: str) -> bool:
    """Identify a standalone line that continues a certification."""
    return bool(
        re.match(
            r"^(?:\(?\s*exam\s+score\s*:|conducted\s+by\b)",
            text.strip(),
            flags=re.IGNORECASE,
        )
    )


def extract_certifications(section: dict) -> dict:
    """
    Extract certifications and activities.

    If a Certifications heading exists, ignore preceding unlabelled text.
    If the parser omitted the nested heading, use the content of this
    canonical section as certification content until Activities/Achievements.
    """
    text = section["original_text"]
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    certifications = []
    activities = []

    has_certifications_heading = any(
        clean_display_text(remove_bullet(line)).casefold().rstrip(":").strip()
        == "certifications"
        for line in lines
    )

    # Keep the strict labelled-section behaviour when the heading exists.
    # Fall back only when the parser has removed that nested heading.
    current_group = None if has_certifications_heading else "certifications"

    exam_score_reason = (
        "Exam-score qualification requires source verification."
    )
    continuation_reason = (
        "A continuation line was merged into this certification; "
        "verify the combined text against the source."
    )

    exam_score_pattern = re.compile(
        r"\bexam\s+score\s*:|"
        r"\d+(?:\.\d+)?\s*%\s+score\s+in\s+the\s+exam\b",
        re.IGNORECASE,
    )

    for line in lines:
        cleaned = clean_display_text(remove_bullet(line))
        label = cleaned.casefold().rstrip(":").strip()

        if label == "certifications":
            current_group = "certifications"
            continue

        if label in {"activities", "achievements"}:
            current_group = "activities"
            continue

        if current_group is None:
            continue

        if current_group == "certifications":
            has_exam_score = bool(exam_score_pattern.search(cleaned))

            is_continuation = bool(
                certifications
                and is_certification_continuation(cleaned)
            )

            if is_continuation:
                previous = certifications[-1]
                previous["name"] += f" {cleaned}"
                previous["source_evidence"] += f" {line}"
                previous["needs_review"] = True

                if continuation_reason not in previous["review_reasons"]:
                    previous["review_reasons"].append(continuation_reason)

                if (
                    has_exam_score
                    and exam_score_reason not in previous["review_reasons"]
                ):
                    previous["review_reasons"].append(exam_score_reason)

                continue

            review_reasons = [exam_score_reason] if has_exam_score else []

            certifications.append({
                "name": cleaned,
                "source_evidence": line,
                "needs_review": bool(review_reasons),
                "review_reasons": review_reasons,
            })

        else:
            activities.append({
                "text": cleaned,
                "source_evidence": line,
            })

    return {
        "certifications": certifications,
        "activities": activities,
        "source_section": text,
    }


def build_entity_output(parsed: dict) -> dict:
    """Build structured output while retaining original section text."""
    sections = parsed["sections"]

    work = (
        extract_work_experience(sections["WORK EXPERIENCE"])
        if "WORK EXPERIENCE" in sections
        else {"records": [], "status": "missing_section"}
    )

    projects = (
        extract_projects(sections["PROJECT WORK"])
        if "PROJECT WORK" in sections
        else {"records": [], "status": "missing_section"}
    )

    skills = (
        extract_skills(sections["SKILLS"])
        if "SKILLS" in sections
        else {"records": [], "status": "missing_section"}
    )

    education = (
        extract_education(sections["EDUCATION"])
        if "EDUCATION" in sections
        else {"records": [], "status": "missing_section"}
    )

    certifications = (
        extract_certifications(sections["CERTIFICATIONS & ACHIEVEMENTS"])
        if "CERTIFICATIONS & ACHIEVEMENTS" in sections
        else {
            "certifications": [],
            "activities": [],
            "status": "missing_section",
        }
    )

    return {
        "schema_version": "1.1",
        "source_file": None,
        "contact": parsed["contact"],
        "work_experience": work,
        "projects": projects,
        "skills": skills,
        "education": education,
        "certifications_and_activities": certifications,
        "source_section_text": {
            name: details["original_text"]
            for name, details in sections.items()
        },
        "parser_validation": parsed["validation"],
        "review_warnings": parsed["review_warnings"],
    }


def main() -> None:
    if len(sys.argv) != 2:
        print(
            'Usage: python structured_entity_extractor.py '
            '"path\\to\\resume.pdf"'
        )
        raise SystemExit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"ERROR: File not found: {file_path}")
        raise SystemExit(1)

    try:
        original_text = extract_text(file_path)

        if not original_text.strip():
            raise ValueError("No readable text was extracted.")

        parsed = parse_resume(original_text)
        result = build_entity_output(parsed)
        result["source_file"] = file_path.name

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / f"{file_path.stem}_entities.json"

        output_file.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"\nInput file: {file_path.name}")
        print(f"Output: {output_file.resolve()}")
        print(
            "Work experience records: "
            f"{len(result['work_experience'].get('records', []))}"
        )
        print(
            "Project records: "
            f"{len(result['projects'].get('records', []))}"
        )
        print(
            "Skill categories: "
            f"{len(result['skills'].get('records', []))}"
        )
        print(
            "Education records: "
            f"{len(result['education'].get('records', []))}"
        )
        print(
            "Certifications: "
            f"{len(result['certifications_and_activities'].get('certifications', []))}"
        )
        print(
            "Activities: "
            f"{len(result['certifications_and_activities'].get('activities', []))}"
        )
        print(f"Review warnings: {len(result['review_warnings'])}")

        if result["work_experience"].get("status") == "needs_review":
            print("WARNING: Work experience extraction needs review.")

        if result["projects"].get("status") == "needs_review":
            print("WARNING: Project extraction needs review.")

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
