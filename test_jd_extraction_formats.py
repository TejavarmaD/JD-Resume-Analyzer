
from jd_analyzer import extract_requirements


def test_extracts_paragraphs_under_unrecognized_heading():
    jd = """
    What You'll Bring

    You have experience building scalable data pipelines.
    You can communicate analytical findings to business stakeholders.
    You are proficient in SQL and Python.
    """

    requirements = extract_requirements(jd)

    texts = [item["requirement"] for item in requirements]

    assert len(texts) == 3
    assert any("data pipelines" in text for text in texts)
    assert any("business stakeholders" in text for text in texts)
    assert any("SQL and Python" in text for text in texts)


def test_extracts_requirements_without_section_headings():
    jd = """
    Develop and maintain SQL queries for business reporting.

    Build dashboards to communicate operational performance.

    Collaborate with stakeholders to understand business needs.
    """

    requirements = extract_requirements(jd)

    assert len(requirements) == 3


def test_extracts_mixed_paragraph_and_bullet_formats():
    jd = """
    Your Profile

    You have experience working with relational databases.

    Responsibilities:
    - Develop automated reporting solutions.
    - Analyze data and identify business trends.
    """

    requirements = extract_requirements(jd)

    texts = [item["requirement"] for item in requirements]

    assert len(texts) == 3
    assert any("relational databases" in text for text in texts)
    assert any("automated reporting" in text for text in texts)
    assert any("business trends" in text for text in texts)


def test_preserves_original_source_section():
    jd = """
    What We Expect

    Demonstrate strong analytical and problem-solving skills.
    """

    requirements = extract_requirements(jd)

    assert len(requirements) == 1
    assert requirements[0]["source_section"] == "what we expect"
    assert (
        requirements[0]["source_evidence"]
        == requirements[0]["requirement"]
    )


def test_does_not_extract_job_metadata_as_requirement():
    jd = """
    Job Title: Data Analyst
    Location: Bengaluru
    Employment Type: Full-time

    Responsibilities

    Develop dashboards using Power BI.
    """

    requirements = extract_requirements(jd)

    assert len(requirements) == 1
    assert "Power BI" in requirements[0]["requirement"]


def test_does_not_extract_job_description_header():
    jd = """
    Job Description: Data Analyst

    Responsibilities:
    Develop dashboards using Power BI.
    """

    requirements = extract_requirements(jd)

    assert len(requirements) == 1
    assert "Power BI" in requirements[0]["requirement"]


def test_does_not_extract_outcome_introductory_sentence():
    jd = """
    Expected Outcomes

    Within the first 6 months, the engineer is expected to:

    Develop and deliver reliable application features.
    """

    requirements = extract_requirements(jd)

    assert len(requirements) == 1
    assert "Develop and deliver" in requirements[0]["requirement"]