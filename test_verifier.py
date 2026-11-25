import json
import unittest
from pathlib import Path

from verifier import score, verify_pairs


class VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(Path("examples/cases.json").read_text(encoding="utf-8"))
        cls.cases = verify_pairs(cls.rows)

    def test_normalized_correct_answer(self):
        result = score(self.cases["route-visible"], "  cedar  GATE ", 0.9)
        self.assertTrue(result["correct_and_supported"])
        self.assertTrue(result["answered"])
        self.assertAlmostEqual(result["brier"], 0.01)

    def test_same_answer_is_unsupported_after_evidence_removal(self):
        result = score(self.cases["route-removed"], "Cedar Gate", 0.9)
        self.assertTrue(result["wrong_if_answered"])
        self.assertAlmostEqual(result["brier"], 0.81)

    def test_abstention_does_not_remove_brier_penalty(self):
        result = score(self.cases["file-visible"], "approved", 0.7)
        self.assertEqual(result["decision"], "[ABSTAIN]")
        self.assertFalse(result["wrong_if_answered"])
        self.assertAlmostEqual(result["brier"], 0.49)

    def test_fail_closed_on_invalid_payload(self):
        for p in [True, "0.9", float("nan"), float("inf"), -1, 2]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                score(self.cases["route-visible"], "Cedar Gate", p)
        for candidate in ["[ABSTAIN]", "", None]:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                score(self.cases["route-visible"], candidate, 0.9)

    def test_reject_duplicate_or_incomplete_pairs(self):
        for rows in [self.rows + [self.rows[0]], self.rows[:-1]]:
            with self.assertRaises(ValueError):
                verify_pairs(rows)

    def test_threshold_tie_is_answered(self):
        self.assertTrue(score(self.cases["file-visible"], "pending", 0.8)["answered"])


if __name__ == "__main__":
    unittest.main()
