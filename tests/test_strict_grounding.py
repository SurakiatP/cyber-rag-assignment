import sys
import os
import unittest
from dotenv import load_dotenv
from langchain_core.documents import Document

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.llm_client import LLMClient

load_dotenv()

class TestStrictGrounding(unittest.TestCase):
    
    def setUp(self):
        self.client = LLMClient()

    def test_out_of_scope_knowledge(self):
        q = "How does Ransomware encrypt files?"
        
        mock_docs = [Document(page_content="Web security covers logging and firewall.", metadata={"source": "thai.pdf", "page": "1"})]
        
        ans = self.client.generate_answer(q, mock_docs)
        print(f"[Q]: {q}\n[A]: {ans}")
        
        refusal_phrases = ["cannot find", "not found", "does not contain"]
        self.assertTrue(any(phrase in ans.lower() for phrase in refusal_phrases), 
                        "Model failed to refuse out-of-domain question.")

    def test_fake_citation_prevention(self):
        q = "What does Section 999 say about passwords?"
        mock_docs = [Document(page_content="Section 1 covers scope. Section 5 covers governance.", metadata={"source": "thai.pdf", "page": "1"})]
        
        ans = self.client.generate_answer(q, mock_docs)
        print(f"[Q]: {q}\n[A]: {ans}")
        
        self.assertTrue("cannot find" in ans.lower(), "Model hallucinated a fake section.")

if __name__ == "__main__":
    unittest.main()