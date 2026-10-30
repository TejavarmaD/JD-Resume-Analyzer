
import unittest

from compare_entity_outputs import (
    classify_source_evidence,
    normalize_metadata,
    normalize_source_text,
)


class TestSourceEvidenceComparison(unittest.TestCase):

    def test_identical_evidence_is_exact_match(self):
        pdf = "• Python, SQL, and data validation"
        docx = "• Python, SQL, and data validation"

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "exact",
        )

    def test_whitespace_difference_is_formatting_only(self):
        pdf = "Python, SQL, and data\nvalidation"
        docx = "Python, SQL, and data validation"

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "formatting_only",
        )

    def test_leading_bullet_difference_is_formatting_only(self):
        pdf = "• Google Data Analytics Certificate - Coursera"
        docx = "Google Data Analytics Certificate - Coursera"

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "formatting_only",
        )

    def test_list_wrapping_and_bullets_are_formatting_only(self):
        pdf = [
            "• Defined the project scope and delivered",
            "an end-to-end contract ETL pipeline.",
        ]
        docx = [
            "Defined the project scope and delivered an end-to-end",
            "contract ETL pipeline.",
        ]

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "formatting_only",
        )

    def test_changed_content_is_reported(self):
        pdf = "Reduced manual review time by 60%."
        docx = "Reduced manual review time by 40%."

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "content_difference",
        )

    def test_missing_words_are_reported(self):
        pdf = "Experience with Python and SQL"
        docx = "Experience with Python"

        self.assertEqual(
            classify_source_evidence(pdf, docx),
            "content_difference",
        )

    def test_metadata_line_wrapping_is_formatting_only(self):
        pdf = {
            "status": "extracted",
            "source_section": (
                "Support global carbon audits across\n"
                "media channels and maintain data quality."
            ),
        }

        docx = {
            "status": "extracted",
            "source_section": (
                "Support global carbon audits across media channels "
                "and maintain data quality."
            ),
        }

        self.assertEqual(
            normalize_metadata(pdf),
            normalize_metadata(docx),
        )

    def test_metadata_bullets_are_formatting_only(self):
        pdf = {
            "source_section": (
                "• Certifications:\n"
                "• Google Data Analytics Certificate"
            ),
        }

        docx = {
            "source_section": (
                "Certifications:\n"
                "Google Data Analytics Certificate"
            ),
        }

        self.assertEqual(
            normalize_metadata(pdf),
            normalize_metadata(docx),
        )

    def test_missing_section_heading_is_detected(self):
        pdf = {
            "source_section": (
                "Certifications:\n"
                "Google Data Analytics Certificate"
            ),
        }

        docx = {
            "source_section": (
                "Google Data Analytics Certificate"
            ),
        }

        self.assertNotEqual(
            normalize_metadata(pdf),
            normalize_metadata(docx),
        )

    def test_missing_content_is_detected_in_metadata(self):
        pdf = {
            "source_section_text": (
                "Support carbon audits and validate emissions data."
            ),
        }

        docx = {
            "source_section_text": (
                "Support carbon audits."
            ),
        }

        self.assertNotEqual(
            normalize_metadata(pdf),
            normalize_metadata(docx),
        )

    def test_source_text_preserves_meaningful_headings(self):
        text = (
            "• Certifications:\n"
            "• Google Data Analytics Certificate\n"
            "• Activities:\n"
            "• Vice-President of Data Science Student Club"
        )

        normalized = normalize_source_text(text)

        self.assertIn("Certifications:", normalized)
        self.assertIn("Activities:", normalized)
        self.assertIn("Google Data Analytics Certificate", normalized)

    def test_metadata_missing_key_is_not_ignored(self):
        pdf = {
            "status": "extracted",
            "source_section": "Certifications: Google Data Analytics",
        }

        docx = {
            "status": "extracted",
        }

        self.assertNotEqual(
            normalize_metadata(pdf),
            normalize_metadata(docx),
        )


if __name__ == "__main__":
    unittest.main()
