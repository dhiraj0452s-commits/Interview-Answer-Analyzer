import unittest
from analyzer.analysis import analyze_answer

class AnalysisTests(unittest.TestCase):
    def test_score_is_in_range(self):
        score, feedback, count = analyze_answer("Tell me about Python", "I developed a Python project successfully.")
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertGreater(count, 0)
        self.assertTrue(feedback)

if __name__ == "__main__": unittest.main()
