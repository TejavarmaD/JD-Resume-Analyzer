import unittest

from evidence_status_engine import build_output, classify_evidence_status


class EvidenceStatusClassificationTests(unittest.TestCase):
    def test_matched_resume_evidence_is_confirmed_but_not_independently_verified(self):
        result = classify_evidence_status({
            "status": "matched",
            "evidence": [{"matched_text": "Python"}],
            "manual_evidence": [],
        })
        self.assertEqual(result["evidence_status"], "confirmed_evidence")
        self.assertEqual(result["evidence_sources"], ["resume_documented"])
        self.assertFalse(result["verification_needed"])

    def test_partial_resume_and_manual_evidence_preserve_both_sources(self):
        result = classify_evidence_status({
            "status": "partial",
            "evidence": [{"matched_text": "documentation"}],
            "manual_evidence": [{"evidence_source": "user_confirmed"}],
            "evidence_groups": [
                {"label": "documentation", "satisfied": True},
                {"label": "code reviews", "satisfied": False},
            ],
        })
        self.assertEqual(result["evidence_status"], "partially_supported")
        self.assertEqual(result["evidence_source_summary"], "both")
        self.assertEqual(result["supported_evidence_groups"], ["documentation"])
        self.assertEqual(result["unsupported_evidence_groups"], ["code reviews"])

    def test_missing_with_related_user_confirmation_is_unverified(self):
        result = classify_evidence_status({
            "status": "missing",
            "evidence": [],
            "manual_evidence": [{"evidence_source": "user_confirmed"}],
        })
        self.assertEqual(result["evidence_status"], "unverified")
        self.assertTrue(result["verification_needed"])

    def test_missing_without_evidence_is_not_interpreted_as_lack_of_capability(self):
        result = classify_evidence_status({
            "status": "missing", "evidence": [], "manual_evidence": []
        })
        self.assertEqual(result["evidence_status"], "no_evidence_found")
        self.assertIn("does not establish lack of capability", result["reason"])

    def test_rejects_unknown_match_status(self):
        with self.assertRaises(ValueError):
            classify_evidence_status({"status": "unknown"})


class EvidenceStatusOutputTests(unittest.TestCase):
    def test_preserves_original_score_and_requirement_status(self):
        evidence = {
            "sources": {"resume_file": "resume.docx"},
            "requirements": [{
                "requirement_id": "REQ-001",
                "requirement_text": "Use Python.",
                "status": "matched",
                "evidence_strength": "documented_proficiency",
                "evidence": [{"matched_text": "Python"}],
                "manual_evidence": [],
            }],
        }
        score = {
            "alignment": {"alignment_score": 21.41, "earned_weight": 20, "total_weight": 93},
            "requirements": [{
                "requirement_id": "REQ-001",
                "requirement": "Use Python.",
                "category": "programming_backend",
                "priority": "must_have",
                "score_points": 1.0,
                "earned_weight": 1.2,
            }],
        }
        output = build_output(evidence, score)
        record = output["requirements"][0]
        self.assertEqual(record["original_match_status"], "matched")
        self.assertEqual(record["original_score_points"], 1.0)
        self.assertEqual(record["original_earned_weight"], 1.2)
        self.assertEqual(output["alignment"]["alignment_score"], 21.41)
        self.assertTrue(output["summary"]["original_matching_score_preserved"])

    def test_rejects_requirement_text_mismatch(self):
        evidence = {"requirements": [{
            "requirement_id": "REQ-001", "requirement_text": "Use Python.",
            "status": "matched", "evidence": [], "manual_evidence": [],
        }]}
        score = {"requirements": [{
            "requirement_id": "REQ-001", "requirement": "Use Java.",
        }]}
        with self.assertRaises(ValueError):
            build_output(evidence, score)


if __name__ == "__main__":
    unittest.main()
