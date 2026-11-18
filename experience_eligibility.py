import json
import re
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RESUME_FILE = (
    BASE_DIR
    / "structured_results"
    / "Tejavarma Dommaraju_Resume_entities.json"
)

OUTPUT_DIR = BASE_DIR / "jd_results"
OUTPUT_FILE = OUTPUT_DIR / "experience_eligibility.json"

REQUIRED_MONTHS = 24

# Relevance and counting decisions are deliberately explicit.
EXPERIENCE_POLICIES = {
    "Omnicom Global Solutions": {
        "experience_type": "full_time",
        "relevance": "relevant",
        "counting_policy": "count",
        "reason": "User confirmed full-time employment. AI agent development responsibilities are relevant to AI engineering.",
    },
    "Johnson Controls": {
        "experience_type": "internship",
        "relevance": "partially_relevant",
        "counting_policy": "review",
        "reason": "IT, data and analytics responsibilities are documented, but their relevance to the JD's specified experience fields requires review.",
    },
}


def parse_month_year(value):
    """Parse dates such as 'Dec 2024' or 'June 2024'."""
    match = re.search(
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\b",
        value,
        re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Unsupported date format: {value}")

    month_text, year_text = match.groups()

    month = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }[month_text[:3].lower()]

    return int(year_text), month


def month_difference(start, end):
    """Return the difference between two year/month pairs."""
    return (end[0] - start[0]) * 12 + end[1] - start[1]


def duration_bounds(start_text, end_text, as_of):
    """
    Return conservative and maximum completed-month estimates.

    Month-only dates do not establish exact start/end days.
    """
    start = parse_month_year(start_text)

    if end_text.lower() == "present":
        end = (as_of.year, as_of.month)
        end_day = as_of.day
    else:
        end = parse_month_year(end_text)
        end_day = 1

    difference = month_difference(start, end)

    # Conservative estimate assumes a late start in the first month.
    minimum = max(0, difference - 1)

    # Maximum estimate assumes an early start in the first month.
    maximum = max(0, difference)

    if end_text.lower() != "present":
        # The end day is also unknown for month-only historical dates.
        maximum = max(0, difference)

    return {
        "minimum_completed_months": minimum,
        "maximum_completed_months": maximum,
        "date_precision": "month",
    }


def split_dates(value):
    """Split a range such as 'Dec 2024 – Present'."""
    parts = re.split(r"\s+[–—-]\s+", value.strip())

    if len(parts) != 2:
        raise ValueError(f"Unsupported date range: {value}")

    return parts[0], parts[1]


def classify_experience(record, as_of):
    employer = record.get("employer", "Unknown employer")
    policy = EXPERIENCE_POLICIES.get(employer)

    if policy is None:
        policy = {
            "experience_type": "other",
            "relevance": "unverified",
            "counting_policy": "review",
            "reason": "No explicit experience policy is configured for this employer.",
        }

    start_text, end_text = split_dates(record["dates"])
    duration = duration_bounds(start_text, end_text, as_of)

    return {
        "employer": employer,
        "job_title": record.get("job_title"),
        "dates": record["dates"],
        "start_date_text": start_text,
        "end_date_text": end_text,
        **policy,
        "duration": duration,
    }


def assess_eligibility(experiences):
    full_time_minimum = 0
    full_time_maximum = 0
    internship_minimum = 0
    internship_maximum = 0
    review_required = False

    for item in experiences:
        duration = item["duration"]

        if item["counting_policy"] == "review":
            review_required = True

        if item["counting_policy"] == "exclude":
            continue

        if item["experience_type"] == "full_time":
            if item["relevance"] == "relevant":
                full_time_minimum += duration["minimum_completed_months"]
                full_time_maximum += duration["maximum_completed_months"]

        elif item["experience_type"] == "internship":
            internship_minimum += duration["minimum_completed_months"]
            internship_maximum += duration["maximum_completed_months"]

    if full_time_minimum >= REQUIRED_MONTHS:
        status = "eligible"
        reason = "At least 24 months of relevant full-time experience are established."

    elif full_time_maximum < REQUIRED_MONTHS and review_required:
        status = "unverified"
        reason = (
            "Full-time experience is below 24 months. "
            "Additional experience has a review-required counting policy."
        )

    elif full_time_maximum < REQUIRED_MONTHS:
        status = "not_eligible"
        reason = "Established relevant full-time experience is below 24 months."

    else:
        status = "unverified"
        reason = "Available date precision does not establish whether 24 months have been completed."

    return {
        "required_experience_months": REQUIRED_MONTHS,
        "eligibility_status": status,
        "reason": reason,
        "full_time_relevant_experience": {
            "minimum_completed_months": full_time_minimum,
            "maximum_completed_months": full_time_maximum,
        },
        "internship_experience": {
            "minimum_completed_months": internship_minimum,
            "maximum_completed_months": internship_maximum,
            "automatically_added_to_full_time": False,
        },
        "review_required": review_required,
    }


def main():
    if not RESUME_FILE.is_file():
        raise FileNotFoundError(f"Resume JSON not found: {RESUME_FILE}")

    data = json.loads(RESUME_FILE.read_text(encoding="utf-8"))
    records = data.get("work_experience", {}).get("records", [])

    as_of = date.today()

    experiences = [
        classify_experience(record, as_of)
        for record in records
    ]

    result = {
        "schema_version": "1.0",
        "evaluation_method": "rule_based_experience_eligibility",
        "as_of_date": as_of.isoformat(),
        "source_file": RESUME_FILE.name,
        "requirement_id": "REQ-047",
        "requirement_text": (
            "Minimum 2 years of relevant experience in Python development, "
            "AI engineering, machine learning engineering or software engineering."
        ),
        "experiences": experiences,
        "assessment": assess_eligibility(experiences),
        "limitations": [
            "Resume dates contain month-level precision, not exact days.",
            "Internship experience is reported separately.",
            "Internship counting policy requires review.",
            "Role relevance is based on configured rules and should be validated.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    assessment = result["assessment"]

    print("EXPERIENCE ELIGIBILITY EVALUATION")
    print("=" * 45)
    print(f"As of date       : {as_of}")
    print(f"Eligibility      : {assessment['eligibility_status']}")
    print(f"Full-time months : {assessment['full_time_relevant_experience']}")
    print(f"Internship months: {assessment['internship_experience']}")
    print(f"Reason           : {assessment['reason']}")
    print(f"Output           : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
