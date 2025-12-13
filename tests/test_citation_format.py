import unittest
import re

class TestCitationFormat(unittest.TestCase):

    def test_regex_matching(self):
        sample_answer_1 = "Firewalls are required [Source: thailand-web-security-standard-2025.pdf, Page: 12b]."
        sample_answer_2 = "Injection is risky [Source: owasp-top-10.pdf, Page: 3]. Persistence maintains access [Source: mitre.pdf, Page: 5a]."
        
        # Pattern: [Source: ..., Page: ...]
        pattern = r"\[Source: .*?, Page: .*?\]"
        
        matches_1 = re.findall(pattern, sample_answer_1)
        self.assertTrue(len(matches_1) == 1, "Failed to detect valid citation format")
        
        matches_2 = re.findall(pattern, sample_answer_2)
        self.assertTrue(len(matches_2) == 2, "Failed to detect multiple citations")

if __name__ == "__main__":
    unittest.main()