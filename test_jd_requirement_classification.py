import unittest

from jd_analyzer import (classify_requirement_type,extract_requirements,is_heading,)


class TestRequirementClassification(unittest.TestCase):

    def test_responsibility_classification(self):
        cases = [
            (
                "Design, develop and maintain LLM-powered applications.",
                "key responsibilities",
            ),
            (
                "Improve retrieval quality through reranking.",
                "key responsibilities",
            ),
            (
                "Participate in code reviews and documentation.",
                "key responsibilities",
            ),
            (
                "Understand when a deterministic workflow is more appropriate than an autonomous agent.",
                "key responsibilities",
            ),
            (
                "Use evaluation and observability tools such as LangSmith, Langfuse or RAGAS.",
                "key responsibilities",
            ),
        ]

        for text, section in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    classify_requirement_type(text, "", section),
                    "responsibility",
                )

    def test_skill_classification(self):
        cases = [
            (
                "Strong proficiency in Python.",
                "programming and backend",
            ),
            (
                "Experience with FastAPI and Flask.",
                "programming and backend",
            ),
            (
                "Experience with Kubernetes and advanced CI/CD practices.",
                "good to have",
            ),
            (
                "Work with SQL and relational databases such as PostgreSQL or MySQL.",
                "required technical skills",
            ),
        ]

        for text, section in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    classify_requirement_type(text, "", section),
                    "skill",
                )

    def test_qualification_classification(self):
        cases = [
            "Minimum 2 years of relevant experience.",
            "Bachelor's degree in Computer Science.",
            "Hands-on experience integrating LLM APIs.",
            "Experience developing at least one working LLM-powered application.",
            "Experience implementing document ingestion and retrieval pipelines.",
        ]

        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    classify_requirement_type(text, "", "experience and education"),
                    "qualification",
                )

    def test_soft_skill_classification(self):
        cases = [
            "Strong problem-solving and analytical thinking.",
            "Clear communication and collaboration skills.",
            "Ability to convert business problems into practical AI solutions.",
        ]

        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    classify_requirement_type(text, "", "what we expect"),
                    "soft_skill",
                )

    def test_outcome_classification(self):
        text = "Build or improve at least one production-oriented RAG pipeline."

        self.assertEqual(
            classify_requirement_type(text, "", "expected outcomes"),
            "outcome",
        )



class TestJDSectionHeadings(unittest.TestCase):

    def test_all_general_headings_are_recognized(self):
        headings = [
            "Core Requirements",
            "Requirements",
            "Key Responsibilities",
            "Roles and Responsibilities",
        ]

        for heading in headings:
            with self.subTest(heading=heading):
                self.assertTrue(is_heading(heading))

    def test_heading_recognition_is_case_insensitive(self):
        headings = [
            "CORE REQUIREMENTS",
            "requirements",
            "KEY RESPONSIBILITIES",
            "roles and responsibilities",
        ]

        for heading in headings:
            with self.subTest(heading=heading):
                self.assertTrue(is_heading(heading))

    def test_heading_recognition_supports_colons_and_numbering(self):
        headings = [
            "Core Requirements:",
            "1. Requirements",
            "2) Key Responsibilities:",
            "3. Roles and Responsibilities:",
        ]

        for heading in headings:
            with self.subTest(heading=heading):
                self.assertTrue(is_heading(heading))

    def test_all_general_headings_extract_requirements(self):
        jd_text = """
Core Requirements
- Strong analytical and problem-solving skills.

Requirements:
- Experience working with SQL databases.

Key Responsibilities
- Develop and maintain data pipelines.

Roles and Responsibilities:
- Collaborate with stakeholders to define business requirements.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 4)

        expected_sections = [
            "core requirements",
            "requirements",
            "key responsibilities",
            "roles and responsibilities",
        ]

        for requirement, expected_section in zip(
            requirements,
            expected_sections,
        ):
            with self.subTest(section=expected_section):
                self.assertEqual(
                    requirement["source_section"],
                    expected_section,
                )
                self.assertEqual(
                    requirement["priority"],
                    "must_have",
                )

    def test_good_to_have_remains_separate(self):
        jd_text = """
Core Requirements
- Strong Python programming skills.

Good to Have
- Experience with Tableau and Power BI.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 2)

        self.assertEqual(
            requirements[0]["priority"],
            "must_have",
        )

        self.assertEqual(
            requirements[1]["priority"],
            "good_to_have",
        )

    def test_headings_are_not_extracted_as_requirements(self):
        jd_text = """
Core Requirements
- Strong communication and collaboration skills.

Key Responsibilities
- Manage stakeholder relationships.
"""

        requirements = extract_requirements(jd_text)

        extracted_texts = [
            item["requirement"]
            for item in requirements
        ]

        self.assertEqual(len(extracted_texts), 2)

        self.assertNotIn("Core Requirements", extracted_texts)
        self.assertNotIn("Key Responsibilities", extracted_texts)



class TestParagraphBasedJDExtraction(unittest.TestCase):

    def test_required_sections_are_recognized(self):
        headings = [
            "Role Summary",
            "Required Qualifications",
            "Preferred Qualifications",
            "Technical Stack Summary",
        ]

        for heading in headings:
            with self.subTest(heading=heading):
                self.assertTrue(is_heading(heading))

    def test_standalone_responsibility_paragraphs_are_extracted(self):
        jd_text = """
Key Responsibilities

Multimodal RAG & Knowledge Systems

Architect production-grade multimodal RAG pipelines
capable of processing unstructured document collections.

AI Agents & Web Automation

Design autonomous AI agents and multi-agent workflows.

Backend & Cloud Architecture

Build scalable asynchronous APIs using Python and FastAPI.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 3)

        self.assertEqual(
            requirements[0]["source_section"],
            "key responsibilities / Multimodal RAG & Knowledge Systems",
        )

        self.assertEqual(
            requirements[1]["source_section"],
            "key responsibilities / AI Agents & Web Automation",
        )

        self.assertEqual(
            requirements[2]["source_section"],
            "key responsibilities / Backend & Cloud Architecture",
        )

    def test_required_qualifications_extract_paragraphs(self):
        jd_text = """
Required Qualifications

Education: Bachelor's degree in Computer Science.

Experience: 2+ years of hands-on experience building
production-grade Generative AI applications.

Programming & Backend: High proficiency in Python,
FastAPI, Asyncio and SQL.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 3)

        for requirement in requirements:
            self.assertEqual(
                requirement["priority"],
                "must_have",
            )

    def test_preferred_qualifications_are_good_to_have(self):
        jd_text = """
Preferred Qualifications

Experience combining knowledge graphs with LLM reasoning.

Familiarity with dynamic UI frameworks.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 2)

        for requirement in requirements:
            self.assertEqual(
                requirement["priority"],
                "good_to_have",
            )

    def test_role_summary_is_not_scored(self):
        jd_text = """
Role Summary

We are seeking an engineer to architect and build
production-grade enterprise AI applications.

Key Responsibilities

Build scalable asynchronous APIs using Python.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 1)

        self.assertIn(
            "Build scalable asynchronous APIs",
            requirements[0]["requirement"],
        )

    def test_technical_stack_summary_is_not_duplicated(self):
        jd_text = """
Required Qualifications

Strong experience with Python and FastAPI.

Technical Stack Summary

Languages & Frameworks: Python, FastAPI, SQL.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 1)

    def test_existing_bullet_extraction_still_works(self):
        jd_text = """
Core Requirements

- Strong analytical and problem-solving skills.

Key Responsibilities

- Develop and maintain data pipelines.

Preferred Qualifications

- Experience with Tableau and Power BI.
"""

        requirements = extract_requirements(jd_text)

        self.assertEqual(len(requirements), 3)

        self.assertEqual(
            requirements[0]["priority"],
            "must_have",
        )

        self.assertEqual(
            requirements[2]["priority"],
            "good_to_have",
        )


if __name__ == "__main__":
    unittest.main()