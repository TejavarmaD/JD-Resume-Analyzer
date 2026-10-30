
import json
import unittest
from pathlib import Path

from structured_entity_extractor import extract_work_experience

RESULTS_DIR = Path("structured_results")

PDF_RESULT = RESULTS_DIR / "Tejavarma Dommaraju(Resume)_entities.json"
DOCX_RESULT = RESULTS_DIR / "Tejavarma Dommaraju_Resume_entities.json"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing output: {path}. Run the entity extractor first."
        )

    return json.loads(path.read_text(encoding="utf-8"))


class TestStructuredResumeEntities(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdf = load_result(PDF_RESULT)
        cls.docx = load_result(DOCX_RESULT)

    def test_both_formats_extract_expected_entity_counts(self):
        for data in (self.pdf, self.docx):
            self.assertEqual(len(data["work_experience"]["records"]), 2)
            self.assertEqual(len(data["projects"]["records"]), 2)
            self.assertEqual(len(data["skills"]["records"]), 5)
            self.assertEqual(len(data["education"]["records"]), 3)
            self.assertEqual(
                len(data["certifications_and_activities"]["certifications"]),
                4,
            )
            self.assertEqual(
                len(data["certifications_and_activities"]["activities"]),
                1,
            )

    def test_skill_categories_match_across_formats(self):
        def categories(data):
            return {
                record["category"]: record["items"]
                for record in data["skills"]["records"]
            }

        self.assertEqual(categories(self.pdf), categories(self.docx))

    def test_expected_recovered_skills_are_present(self):
        categories = {
            record["category"]: record["items"]
            for record in self.pdf["skills"]["records"]
        }

        self.assertIn(
            "emissions data validation",
            categories["Sustainability & ESG"],
        )
        self.assertIn(
            "carbon audit support",
            categories["Sustainability & ESG"],
        )
        self.assertIn(
            "data transformation",
            categories["Data Analytics & Processing"],
        )
        self.assertIn(
            "Retrieval-Augmented Generation (RAG)",
            categories["Automation & AI"],
        )

    def test_uncertain_framework_claim_is_flagged_in_both_formats(self):
        for data in (self.pdf, self.docx):
            frameworks = next(
                record
                for record in data["skills"]["records"]
                if record["category"] == "Sustainability Frameworks"
            )

            self.assertTrue(frameworks["needs_review"])
            self.assertTrue(
                any(
                    "confirmation" in reason.lower()
                    for reason in frameworks["review_reasons"]
                )
            )
            self.assertIn(
                "if accurate",
                frameworks["source_evidence"].lower(),
            )

    # NEW REGRESSION TEST
    def test_drafting_note_is_not_extracted_as_a_skill(self):
        for data in (self.pdf, self.docx):
            frameworks = next(
                record
                for record in data["skills"]["records"]
                if record["category"] == "Sustainability Frameworks"
            )

            # The drafting note must not appear in the extracted skills.
            self.assertNotIn(
                "if accurate",
                [item.lower() for item in frameworks["items"]],
            )

            # Preserve the original wording for auditability.
            self.assertIn(
                "if accurate",
                frameworks["source_evidence"].lower(),
            )

            # Keep the review flag because the claim needs confirmation.
            self.assertTrue(frameworks["needs_review"])

    def test_original_source_sections_are_preserved(self):
        for data in (self.pdf, self.docx):
            self.assertIn("SKILLS", data["source_section_text"])
            self.assertTrue(data["source_section_text"]["SKILLS"].strip())
            self.assertTrue(data["skills"]["source_section"].strip())

    def test_certification_exam_score_requires_review(self):
        for data in (self.pdf, self.docx):
            certifications = data["certifications_and_activities"][
                "certifications"
            ]

            flagged = [
                cert for cert in certifications
                if cert["needs_review"]
            ]

            self.assertTrue(
                any(
                    "exam score" in cert["name"].lower()
                    or "score in the exam" in cert["name"].lower()
                    for cert in flagged
                ),
                "The exam-score qualification should be flagged.",
            )

    def test_project_source_evidence_is_retained(self):
        for data in (self.pdf, self.docx):
            projects = data["projects"]["records"]

            self.assertEqual(len(projects), 2)

            for project in projects:
                self.assertTrue(project["name"])
                self.assertTrue(project["source_evidence"])
                self.assertTrue(project["evidence"])

        # Known PDF extraction anomaly: preserve and detect it.
        pdf_project_text = " ".join(
            line
            for project in self.pdf["projects"]["records"]
            for line in project["source_evidence"]
        ).lower()

        self.assertIn("rates.", pdf_project_text)
        self.assertNotIn("rates.n", pdf_project_text)

    def test_suspicious_pdf_project_text_is_flagged(self):
        revenue_project = next(
            project
            for project in self.pdf["projects"]["records"]
            if "Revenue Insights" in project["name"]
        )

        self.assertFalse(revenue_project["needs_review"])
        self.assertNotIn(
            "Possible PDF extraction artifact: evidence ends with '.n'. "
            "Verify against the original document.",
            revenue_project["review_reasons"],
        )

        # The original suspicious text must remain available.
        evidence = " ".join(revenue_project["evidence"]).lower()
        self.assertIn("rates.", evidence)
        self.assertNotIn("rates.n", evidence)

    def test_pdf_wrapped_responsibility_lines_are_joined(self):
        section = {
            "original_text": (
                "Omnicom Global Solutions, Bangalore Dec 2024 – Present\n"
                "Associate\n"
                "• Support global carbon audits across\n"
                "media channels and validate emissions data.\n"
                "• Develop AI agents for workflow automation.\n"
            )
        }

        result = extract_work_experience(section)
        record = result["records"][0]

        self.assertEqual(len(record["responsibilities"]), 2)
        self.assertEqual(
            record["responsibilities"][0],
            "Support global carbon audits across media channels "
            "and validate emissions data.",
        )
        self.assertEqual(
            record["responsibilities"][1],
            "Develop AI agents for workflow automation.",
        )

    def test_new_bullet_starts_a_new_responsibility(self):
        section = {
            "original_text": (
                "Johnson Controls, Bangalore Jan 2024 - June 2024\n"
                "IT Data and Analytics Intern\n"
                "• Developed a Power Apps interface.\n"
                "• Integrated Power Automate into reporting workflows.\n"
            )
        }

        result = extract_work_experience(section)
        record = result["records"][0]

        self.assertEqual(len(record["responsibilities"]), 2)
        self.assertEqual(
            record["responsibilities"][0],
            "Developed a Power Apps interface.",
        )
        self.assertEqual(
            record["responsibilities"][1],
            "Integrated Power Automate into reporting workflows.",
        )

    def test_source_evidence_is_preserved_when_lines_are_joined(self):
        source_lines = [
            "Omnicom Global Solutions, Bangalore Dec 2024 – Present",
            "Associate",
            "• Support global carbon audits across",
            "media channels and validate emissions data.",
        ]
        section = {"original_text": "\n".join(source_lines)}

        result = extract_work_experience(section)
        record = result["records"][0]

        self.assertEqual(record["source_evidence"], source_lines)
        self.assertEqual(len(record["responsibilities"]), 1)
        self.assertIn(
            "Support global carbon audits across media channels",
            record["responsibilities"][0],
        )

    def test_education_fields_match_across_formats(self):
        for data in (self.pdf, self.docx):
            records = data["education"]["records"]

            institution = next(
                r for r in records if r["record_type"] == "institution"
            )
            degree = next(
                r for r in records if r["record_type"] == "degree"
            )
            honors = next(
                r for r in records if r["record_type"] == "honors"
            )

            self.assertEqual(institution["institution"], "Jain University")
            self.assertEqual(
                institution["school"],
                "School of Engineering and Technology",
            )
            self.assertEqual(institution["location"], "Bangalore")
            self.assertEqual(
                institution["dates"], "June 2020 - May 2024"
            )

            self.assertEqual(degree["degree"], "Bachelor of Technology")
            self.assertEqual(
                degree["field_of_study"],
                "CSE (majoring in Data Science)",
            )
            self.assertEqual(degree["grade"], "8.2/10")
            self.assertEqual(
                honors["honors"],
                "Honors in Data Science (specialization)",
            )

    def test_education_source_evidence_is_preserved(self):
        for data in (self.pdf, self.docx):
            education = data["education"]

            self.assertIn("Jain University", education["source_section"])
            self.assertEqual(len(education["records"]), 3)

            for record in education["records"]:
                self.assertTrue(record["source_evidence"])
                self.assertTrue(record["text"])

    def test_education_honors_are_linked_without_losing_source_record(self):
        for data in (self.pdf, self.docx):
            records = data["education"]["records"]

            degree = next(
                r for r in records if r["record_type"] == "degree"
            )
            honors = next(
                r for r in records if r["record_type"] == "honors"
            )

            self.assertEqual(degree["honors"], honors["honors"])
            self.assertEqual(
                honors["source_evidence"],
                "Honors in Data Science (specialization)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
