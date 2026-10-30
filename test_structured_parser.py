
import sys
import unittest
from pathlib import Path

from structured_resume_parser import extract_text, parse_resume


RESUME_DIR = Path(
    r"C:\Users\tejavarma.dommaraju\OneDrive - OneWorkplace\Desktop\Resume"
)

RESUME_FILES = [
    RESUME_DIR / "Tejavarma Dommaraju(Resume).pdf",
    RESUME_DIR / "Tejavarma Dommaraju_Resume.docx",
]

EXPECTED_SECTIONS = {
    "EXECUTIVE SUMMARY",
    "WORK EXPERIENCE",
    "PROJECT WORK",
    "SKILLS",
    "EDUCATION",
    "CERTIFICATIONS & ACHIEVEMENTS",
}


class TestStructuredResumeParser(unittest.TestCase):

    def test_both_resume_files_exist(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                self.assertTrue(file_path.is_file())

    def test_both_formats_extract_all_sections(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                result = parse_resume(extract_text(file_path))

                self.assertEqual(
                    set(result["sections"].keys()),
                    EXPECTED_SECTIONS,
                )
                self.assertEqual(
                    result["validation"]["missing_expected_sections"],
                    [],
                )
                self.assertTrue(
                    result["validation"]["section_order_valid"]
                )

    def test_contact_fields_are_extracted(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                result = parse_resume(extract_text(file_path))
                contact = result["contact"]

                self.assertEqual(
                    contact["name"],
                    "TEJAVARMA DOMMARAJU",
                )
                self.assertIsNotNone(contact["email"])
                self.assertIsNotNone(contact["phone"])
                self.assertIsNotNone(contact["github_url"])

    def test_original_and_normalized_text_are_separate(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                result = parse_resume(extract_text(file_path))

                for section in result["sections"].values():
                    self.assertIn("original_text", section)
                    self.assertIn("normalized_text", section)

                    self.assertIsInstance(
                        section["original_text"], str
                    )
                    self.assertIsInstance(
                        section["normalized_text"], str
                    )
                    self.assertTrue(
                        section["original_text"].strip()
                    )
                    self.assertTrue(
                        section["normalized_text"].strip()
                    )

    def test_uncertain_claim_is_flagged(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                result = parse_resume(extract_text(file_path))

                warning_types = {
                    warning["type"]
                    for warning in result["review_warnings"]
                }

                self.assertIn(
                    "uncertain_claim", warning_types
                )
                self.assertIn(
                    "qualification_requires_confirmation",
                    warning_types,
                )

    def test_source_text_is_retained(self):
        for file_path in RESUME_FILES:
            with self.subTest(file=file_path.name):
                original = extract_text(file_path)
                result = parse_resume(original)

                self.assertEqual(
                    result["source"]["original_extracted_text"],
                    original,
                )
                self.assertEqual(
                    result["source"]["extracted_character_count"],
                    len(original),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
