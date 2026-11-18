import unittest

from skill_tag_extractor import (
    compile_dictionary,
    find_matches,
    find_unmatched_terms,
)


class TestUnmatchedTermDetection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.patterns = compile_dictionary()

    def detect(self, requirement_text):
        matches = find_matches(requirement_text, self.patterns)

        return find_unmatched_terms(
            requirement_text,
            matches,
        )

    def test_unmatched_technical_terms_are_detected(self):
        text = "Implement JWT authentication using gRPC microservices."

        unmatched = self.detect(text)
        detected_terms = [item["term"] for item in unmatched]

        self.assertIn("JWT", detected_terms)
        self.assertNotIn("authentication", detected_terms)
        self.assertIn("gRPC", detected_terms)
        self.assertIn("microservices", detected_terms)

    def test_matched_dictionary_terms_are_not_unmatched(self):
        text = "Develop applications using Python and JWT."

        unmatched = self.detect(text)
        detected_terms = [item["term"].lower() for item in unmatched]

        self.assertNotIn("python", detected_terms)
        self.assertIn("jwt", detected_terms)

    def test_evidence_offsets_and_exact_text(self):
        text = "Implement JWT authentication."

        unmatched = self.detect(text)

        jwt_term = next(
            item for item in unmatched
            if item["term"] == "JWT"
        )

        evidence = jwt_term["evidence"]

        self.assertEqual(
            text[evidence["start"]:evidence["end"]],
            "JWT",
        )
        self.assertEqual(evidence["matched_text"], "JWT")
        self.assertEqual(evidence["start"], 10)
        self.assertEqual(evidence["end"], 13)

    def test_duplicate_candidates_are_not_returned(self):
        text = "Use JWT for authentication."

        unmatched = self.detect(text)
        jwt_matches = [
            item for item in unmatched
            if item["term"] == "JWT"
        ]
        self.assertEqual(len(jwt_matches), 1)

    def test_all_unmatched_terms_require_manual_review(self):
        text = "Implement JWT authentication for microservices."

        unmatched = self.detect(text)

        self.assertTrue(unmatched)

        for item in unmatched:
            self.assertEqual(
                item["review_status"],
                "needs_manual_review",
            )


if __name__ == "__main__":
    unittest.main()
