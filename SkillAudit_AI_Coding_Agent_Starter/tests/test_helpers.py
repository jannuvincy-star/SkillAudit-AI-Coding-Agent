import unittest
from agent import clean_code, run_python

class AgentHelperTests(unittest.TestCase):
    def test_strips_markdown_fences(self):
        self.assertEqual(clean_code("```python\nprint('ok')\n```"), "print('ok')\n")

    def test_successful_subprocess(self):
        result = run_python("print('PASS')\n")
        self.assertTrue(result["passed"])
        self.assertIn("PASS", result["stdout"])

    def test_nonzero_exit(self):
        result = run_python("raise ValueError('expected')\n")
        self.assertFalse(result["passed"])
        self.assertIn("ValueError", result["stderr"])

if __name__ == "__main__":
    unittest.main()
