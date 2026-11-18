
import unittest

from skill_tag_extractor import (
    compile_dictionary,
    find_matches,
    build_skill_tags,
    extract_alternatives,
    build_requirement_output,
    build_summary,
)


class TestSkillTagExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.patterns = compile_dictionary()

    def extract(self, text):
        matches = find_matches(text, self.patterns)
        return matches

    def test_python_is_detected(self):
        matches = self.extract("Build applications using Python.")

        self.assertIn(
            "python",
            [match["tag"] for match in matches],
        )

    def test_matching_is_case_insensitive(self):
        matches = self.extract("Use PYTHON and fastapi.")

        tags = [match["tag"] for match in matches]

        self.assertIn("python", tags)
        self.assertIn("fastapi", tags)

    def test_evidence_offsets_are_correct(self):
        text = "Build applications using Python."
        matches = self.extract(text)

        python_match = next(
            match for match in matches
            if match["tag"] == "python"
        )

        self.assertEqual(
            text[python_match["start"]:python_match["end"]],
            "Python",
        )

    def test_evidence_offsets_are_zero_based(self):
        text = "Python"
        matches = self.extract(text)

        self.assertEqual(matches[0]["start"], 0)
        self.assertEqual(matches[0]["end"], 6)

    def test_longest_overlapping_alias_is_preferred(self):
        text = "Use Azure OpenAI."
        matches = self.extract(text)

        overlapping_matches = [
            match for match in matches
            if match["start"] < 15 and match["end"] > 4
        ]

        self.assertEqual(len(overlapping_matches), 1)
        self.assertEqual(
            overlapping_matches[0]["tag"],
            "azure_openai",
        )

    def test_rag_does_not_match_inside_ragas(self):
        matches = self.extract("Use RAGAS for evaluation.")

        tags = [match["tag"] for match in matches]

        self.assertIn("ragas", tags)
        self.assertNotIn("rag", tags)

    def test_lora_does_not_match_inside_qlora(self):
        matches = self.extract("Fine-tune models using QLoRA.")

        tags = [match["tag"] for match in matches]

        self.assertIn("qlora", tags)
        self.assertNotIn("lora", tags)

    def test_multiple_occurrences_are_preserved(self):
        text = "Use Python with Python-based applications."
        matches = self.extract(text)

        python_matches = [
            match for match in matches
            if match["tag"] == "python"
        ]

        self.assertEqual(len(python_matches), 2)

    def test_skill_tags_group_multiple_evidence_occurrences(self):
        text = "Use Python with Python-based applications."
        matches = self.extract(text)

        skill_tags = build_skill_tags(matches, text)

        python_tag = next(
            item
            for item in skill_tags["technologies"]
            if item["tag"] == "python"
        )

        self.assertEqual(len(python_tag["evidence"]), 2)

        for evidence in python_tag["evidence"]:
            self.assertEqual(
                text[evidence["start"]:evidence["end"]],
                evidence["matched_text"],
            )

    def test_skill_tags_include_all_categories(self):
        skill_tags = build_skill_tags([], "")

        self.assertEqual(
            set(skill_tags),
            {"concepts", "technologies", "platforms", "standards"},
        )

        for category in skill_tags:
            self.assertEqual(skill_tags[category], [])

    def test_or_alternatives_are_detected(self):
        text = "Use FAISS or Chroma for vector search."
        matches = self.extract(text)

        alternatives = extract_alternatives(text, matches)

        self.assertTrue(
            any(
                alternative["operator"] == "OR"
                and set(alternative["tags"]) == {"faiss", "chroma"}
                for alternative in alternatives
            )
        )

    def test_and_is_not_treated_as_or(self):
        text = "Use Python and FastAPI."
        matches = self.extract(text)

        alternatives = extract_alternatives(text, matches)

        self.assertEqual(alternatives, [])

    def test_requirement_output_structure(self):
        record = {
            "id": "REQ-TEST",
            "requirement": "Build applications using Python.",
        }

        output = build_requirement_output(record, self.patterns)

        self.assertEqual(output["requirement_id"], "REQ-TEST")
        self.assertEqual(
            output["requirement_text"],
            record["requirement"],
        )

        self.assertEqual(
            set(output["skill_tags"]),
            {"concepts", "technologies", "platforms", "standards"},
        )

        self.assertIn("alternatives", output)
        self.assertIn("unmatched_terms", output)

    def test_missing_requirement_text_is_rejected(self):
        record = {
            "id": "REQ-TEST",
            "requirement": "",
        }

        with self.assertRaises(ValueError):
            build_requirement_output(record, self.patterns)

    def test_summary_counts_requirements_and_tags(self):
        records = [
            {
                "skill_tags": {
                    "concepts": [],
                    "technologies": [
                        {
                            "tag": "python",
                            "evidence": [
                                {"start": 0, "end": 6},
                                {"start": 10, "end": 16},
                            ],
                        }
                    ],
                    "platforms": [],
                    "standards": [],
                }
            },
            {
                "skill_tags": {
                    "concepts": [],
                    "technologies": [],
                    "platforms": [],
                    "standards": [],
                }
            },
        ]

        summary = build_summary(records)

        self.assertEqual(summary["total_requirements"], 2)
        self.assertEqual(summary["requirements_with_tags"], 1)
        self.assertEqual(summary["requirements_without_tags"], 1)
        self.assertEqual(summary["total_tag_occurrences"], 2)
        self.assertEqual(summary["total_unique_tags"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
