
import pytest

from jd_analyzer import extract_requirements


@pytest.mark.parametrize(
    "jd_text, expected_phrases, expected_sections",
    [
        (
            """
            Job Title: Data Analyst
            Location: Bengaluru

            About the Role

            We are looking for an analyst to turn business data into
            actionable insights.

            Responsibilities

            - Analyze large datasets using SQL and Python.
            - Develop dashboards and reports using Power BI.
            - Identify trends and communicate findings to stakeholders.

            Required Qualifications

            - Strong SQL skills and experience with data analysis.
            - Knowledge of Excel and data visualization.
            - Bachelor's degree in a relevant discipline.
            """,
            [
                "Analyze large datasets using SQL and Python.",
                "Develop dashboards and reports using Power BI.",
                "Identify trends and communicate findings to stakeholders.",
                "Strong SQL skills and experience with data analysis.",
                "Knowledge of Excel and data visualization.",
                "Bachelor's degree in a relevant discipline.",
            ],
            [
                "responsibilities",
                "required qualifications",
            ],
        ),
        (
            """
            Product Manager

            Role Summary

            You will shape the product strategy and deliver meaningful
            customer outcomes.

            What You'll Do

            - Define and communicate the product roadmap.
            - Prioritize features using customer feedback and business impact.
            - Collaborate with engineering, design and business teams.

            What We're Looking For

            - Experience managing products through their lifecycle.
            - Strong stakeholder management and communication skills.
            - Ability to use data to guide product decisions.

            Preferred Qualifications

            Experience with agile product development.
            """,
            [
                "Define and communicate the product roadmap.",
                "Prioritize features using customer feedback and business impact.",
                "Collaborate with engineering, design and business teams.",
                "Experience managing products through their lifecycle.",
                "Strong stakeholder management and communication skills.",
                "Ability to use data to guide product decisions.",
                "Experience with agile product development.",
            ],
            [
                "what you'll do",
                "what we're looking for",
                "preferred qualifications",
            ],
        ),
        (
            """
            Software Engineer

            About the Position

            We are looking for an engineer to build reliable software systems.

            Key Responsibilities

            - Design and develop backend services using Python.
            - Build and maintain REST APIs.
            - Write automated tests and troubleshoot production issues.

            Minimum Qualifications

            - Strong programming fundamentals.
            - Experience with databases and SQL.
            - Understanding of system design and software architecture.

            Nice to Have

            Experience deploying applications using Docker and cloud platforms.
            """,
            [
                "Design and develop backend services using Python.",
                "Build and maintain REST APIs.",
                "Write automated tests and troubleshoot production issues.",
                "Strong programming fundamentals.",
                "Experience with databases and SQL.",
                "Understanding of system design and software architecture.",
                "Experience deploying applications using Docker and cloud platforms.",
            ],
            [
                "key responsibilities",
                "minimum qualifications",
                "nice to have",
            ],
        ),
    ],
)
def test_extracts_requirements_across_different_roles(
    jd_text,
    expected_phrases,
    expected_sections,
):
    requirements = extract_requirements(jd_text)

    extracted_texts = [
        item.get("requirement", item.get("requirement_text", ""))
        for item in requirements
    ]

    extracted_sections = {
        item.get("source_section", "")
        for item in requirements
    }

    assert requirements, "No requirements were extracted."

    for phrase in expected_phrases:
        assert any(
            phrase.casefold() in text.casefold()
            for text in extracted_texts
        ), f"Expected requirement was not extracted: {phrase}"

    for section in expected_sections:
        assert section in extracted_sections, (
            f"Expected source section was not preserved: {section}"
        )


def test_does_not_extract_metadata_as_requirements():
    jd_text = """
    Job Title: Product Manager
    Location: Bengaluru
    Employment Type: Full-time
    Department: Product

    Responsibilities

    - Define and manage the product roadmap.
    """

    requirements = extract_requirements(jd_text)

    assert len(requirements) == 1
    assert "product roadmap" in requirements[0]["requirement"].casefold()


def test_keeps_requirements_from_separate_sections_distinct():
    jd_text = """
    Responsibilities

    - Develop backend services using Python.

    Required Qualifications

    - Experience with Python programming.
    """

    requirements = extract_requirements(jd_text)

    assert len(requirements) == 2

    sections = [item["source_section"] for item in requirements]

    assert sections == [
        "responsibilities",
        "required qualifications",
    ]
