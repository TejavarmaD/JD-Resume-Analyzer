import unittest

from structured_entity_extractor import split_pdf_wrapped_text, extract_certifications


class TestResumeTextGeneralization(unittest.TestCase):
    def test_wrapped_sentence_is_joined(self):
        text = (
            "Built a data validation workflow that improved reporting\n"
            "consistency across multiple sources."
        )
        self.assertEqual(
            split_pdf_wrapped_text(text),
            ["Built a data validation workflow that improved reporting consistency across multiple sources."],
        )

    def test_new_bullet_starts_new_record(self):
        text = (
            "• Built a Python data pipeline.\n"
            "• Automated reporting checks."
        )
        result = split_pdf_wrapped_text(text)
        self.assertEqual(len(result), 2)
        self.assertIn("Built a Python data pipeline.", result[0])
        self.assertIn("Automated reporting checks.", result[1])

    
    def test_section_heading_is_not_joined_to_previous_text(self):
        text = "Built dashboards for stakeholders.\nEDUCATION\nBachelor of Technology"
        result = split_pdf_wrapped_text(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Built dashboards for stakeholders.")
        self.assertEqual(result[1], "EDUCATION Bachelor of Technology")

    def test_empty_lines_do_not_create_empty_records(self):
        text = "Built a data pipeline.\n\n\nAutomated quality checks.\n"
        self.assertEqual(
            split_pdf_wrapped_text(text),
            ["Built a data pipeline. Automated quality checks."],
        )

    def test_wrapped_nptel_credential_is_one_certification(self):
        section = {
            "original_text": (
                "Certifications:\n"
                "NPTEL certification on Python for Data Science with 69% score in the Exam\n"
                "conducted by IITM - NPTEL (Exam score: >60%)\n"
                "Activities:\n"
                "Vice-President of Data Science Student Club for 10 months."
            )
        }
        result = extract_certifications(section)
        self.assertEqual(len(result["certifications"]), 1)
        self.assertIn("NPTEL certification on Python for Data Science", result["certifications"][0]["name"])
        self.assertIn("Exam score: >60%", result["certifications"][0]["name"])
        self.assertEqual(len(result["activities"]), 1)
        self.assertIn("Vice-President", result["activities"][0]["text"])

    def test_unlabelled_text_is_not_assumed_to_be_a_certification(self):
        section = {
            "original_text": (
                "NPTEL certification on Python for Data Science\n"
                "Certifications:\n"
                "Google Data Analytics Certificate - Coursera"
            )
        }
        result = extract_certifications(section)
        self.assertEqual(
            [item["name"] for item in result["certifications"]],
            ["Google Data Analytics Certificate - Coursera"],
        )

    def test_certification_and_activity_groups_are_separated(self):
        section = {
            "original_text": (
                "Certifications:\n"
                "Google Data Analytics Certificate - Coursera\n"
                "Activities:\n"
                "Vice-President of Data Science Student Club for 10 months."
            )
        }
        result = extract_certifications(section)
        self.assertEqual(len(result["certifications"]), 1)
        self.assertEqual(len(result["activities"]), 1)
        self.assertNotIn("Vice-President", result["certifications"][0]["name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)