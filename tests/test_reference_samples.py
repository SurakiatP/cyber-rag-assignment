import sys
import os
import unittest
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_engine import RAGEngine
from src.llm_client import LLMClient

load_dotenv()

class TestReferenceSamples(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.rag = RAGEngine()
        cls.llm = LLMClient()
        if not cls.rag.load_index():
            raise RuntimeError("Database not loaded. Please run app.py or build_index first.")

    def _run_query(self, question):
        print(f"\n[Q]: {question}")
        expanded = self.llm.expand_query(question)
        docs = self.rag.search(expanded)
        answer = self.llm.generate_answer(question, docs)
        print(f"[A]: {answer}\n" + "-"*50)
        return answer

    def test_q1_owasp_broken_access_control(self):
        # Ref Q1: What is Broken Access Control according to OWASP?
        ans = self._run_query("What is Broken Access Control according to OWASP?")
        # Check only if the correct source is cited
        self.assertIn("owasp-top-10.pdf", ans)

    def test_q2_thai_web_security(self):
        # Ref Q2: What website security controls are required by the Thailand Web Security Standard?
        ans = self._run_query("What website security controls are required by the Thailand Web Security Standard?")
        self.assertIn("thailand-web-security-standard-2025.pdf", ans)

    def test_q3_mitre_tactic_vs_technique(self):
        # Ref Q3: What is the difference between a Tactic and a Technique in MITRE ATT&CK?
        ans = self._run_query("What is the difference between a Tactic and a Technique in MITRE ATT&CK?")
        self.assertIn("mitre-attack-philosophy-2020.pdf", ans)

    def test_q4_owasp_injection_mitigation(self):
        # Ref Q4: What mitigation steps does OWASP recommend for Injection vulnerabilities?
        ans = self._run_query("What mitigation steps does OWASP recommend for Injection vulnerabilities?")
        self.assertIn("owasp-top-10.pdf", ans)

    def test_q5_mitre_persistence(self):
        # Ref Q5: How does MITRE describe the purpose of Persistence techniques?
        ans = self._run_query("How does MITRE describe the purpose of Persistence techniques?")
        self.assertIn("mitre-attack-philosophy-2020.pdf", ans)

if __name__ == "__main__":
    unittest.main()