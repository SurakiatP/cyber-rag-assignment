import os
import logging
import re
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name=None):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        default_model = os.getenv("LLM_MODEL_NAME", "gemma3:4b")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        timeout = float(os.getenv("LLM_TIMEOUT", "120.0"))
        
        self.model_name = model_name or default_model
        
        logger.info(f"Initializing ChatOllama (Model: {self.model_name}) at {base_url}...")
        
        self.llm = ChatOllama(
            model=self.model_name,
            base_url=base_url,
            temperature=temperature,
            keep_alive="1h",
            num_predict=512,
            request_timeout=timeout
        )

    def expand_query(self, query: str) -> str:
        logger.info(f"Expanding query: '{query}'")
        
        system_prompt = """You are a bilingual search query optimizer (Thai/English). **YOU ARE NOT A CHATBOT.**

Your goal: Extract technical keywords and provide translations to help a search engine find relevant documents.

=== STEP-BY-STEP PROCESS ===

STEP 1: ANALYZE THE QUERY
- Read the user query carefully
- Identify the main technical concepts

STEP 2: EXTRACT CORE KEYWORDS
- Extract 2-3 core technical terms from the query
- Preserve acronyms exactly as they appear (e.g., OWASP, API, SQL, MITRE, ATT&CK, MFA, 2FA)
- Preserve transliterated terms exactly as written

STEP 3: TRANSLATE KEYWORDS
- If query is in English → Translate to Thai
- If query is in Thai → Translate to English
- Keep technical acronyms in their original form (don't translate acronyms)

STEP 4: ADD SYNONYMS (If Applicable)
- Add 1-2 relevant synonyms for each language
- Synonyms should be commonly used alternatives

STEP 5: FORMAT YOUR OUTPUT
- Combine all keywords (Thai + English) into one list
- Separate each keyword with a comma and space
- Do NOT write full sentences
- Do NOT explain your choices
- Do NOT use double quotes around the output

=== OUTPUT REQUIREMENTS ===

Your output MUST contain:
- 1-3 keywords in Thai
- 1-3 keywords in English

Total: 2-6 keywords combined

=== EXAMPLES ===

Example 1:
Query: "What is log retention?"
Output: การเก็บ log, การจัดเก็บบันทึก, ระยะเวลาเก็บ log, log retention, log storage, retention period

Example 2:
Query: "What is OWASP Top 10"
Output: OWASP Top 10, มาตรฐาน OWASP, OWASP, Top 10

Example 3:
Query: "How to implement MFA?"
Output: การใช้งาน MFA, การยืนยันตัวตน, MFA

Example 4:
Query: "MITRE ATT&CK framework มีประโยชน์อย่างไร"
Output: MITRE ATT&CK, กรอบการทำงาน MITRE, เทคนิคการโจมตี, MITRE ATT&CK framework

=== CRITICAL REMINDERS ===

1. Output format: keyword1, keyword2, keyword3, keyword4, keyword5, keyword6
2. NO explanations - keywords only
3. NO full sentences
4. Preserve acronyms exactly (OWASP, not โอวาสป์)
5. Mix Thai and English keywords in the output
6. Total 2-6 keywords (balanced between both languages)

Now process this query:"""

        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            keywords = chain.invoke({"query": query})
            keywords = keywords.replace('\n', ' ').replace('"', '').strip()
            keywords = re.sub(r'(Here is|The translation|However).*', '', keywords, flags=re.IGNORECASE)
            
            expanded_query = f"{query} {keywords}"
            logger.info(f"Expanded: {expanded_query}")
            return expanded_query
        except Exception as e:
            logger.error(f"Expansion failed: {e}")
            return query 

    def generate_answer(self, query: str, context_docs: List[Document]) -> str:
        if not context_docs:
            return "I cannot find relevant information in the provided documents."

        logger.info(f"Generating answer from {len(context_docs)} documents...")

        context_text = ""
        for i, doc in enumerate(context_docs):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("logical_page", "-")
            content = doc.page_content.replace("\n", " ").strip()
            content = content.replace("{", "{{").replace("}", "}}")
            
            context_text += f"\n--- Document {i+1} (Source: {source}, Page: {page}) ---\n{content}\n"

        system_prompt = """You are a Cybersecurity Auditor analyzing documents.

=== YOUR MISSION ===
Answer questions using ONLY the Context provided below. Never use outside knowledge.

=== STEP-BY-STEP PROCESS ===

STEP 1: READ THE CONTEXT
- Read all Context chunks carefully
- The Context contains both Thai and English text
- Understand information from both languages

STEP 2: SEARCH FOR THE ANSWER
- Look for information that directly answers this question: "{question}"
- Check if the Context contains the specific answer

STEP 3: DECIDE YOUR ACTION
→ If you FOUND the answer in Context:
  - Go to STEP 4
  
→ If you CANNOT find the answer in Context:
  - Stop here
  - Reply exactly: "I cannot find this information in the provided documents."
  - Do NOT go to STEP 4

STEP 4: EXTRACT THE INFORMATION
- Copy the relevant facts from Context
- Translate Thai content to English if needed
- Keep your answer brief (maximum 3-4 key points)
- Use clear, simple language

STEP 5: ADD CITATIONS
- Every fact MUST have a citation at the END
- Format: [Source: filename.pdf, Page: X]
- If multiple sources support the same fact, list all of them:
  [Source: file1.pdf, Page: 1], [Source: file2.pdf, Page: 5]

STEP 6: WRITE YOUR FINAL ANSWER
- State the facts directly (no "According to..." phrases)
- Put citation at the end of each fact
- Concise, easy to understand, and to the point
- Answer in English only (no Thai text)
- Double-check: Does every fact have a citation?

=== FORMAT EXAMPLES ===

✓ CORRECT FORMAT:
"Multi-factor authentication is required for all admin accounts [Source: security-policy.pdf, Page: 3]."

✗ WRONG FORMATS:
- "MFA is required." → Missing citation
  
- "[Source: policy.pdf] MFA is required." → Citation must be at the END, not the beginning
  
- "According to the document, MFA is required [Source: policy.pdf, Page: 3]." → Don't use "According to..." phrases
  
- "ต้องใช้ MFA [Source: policy.pdf, Page: 3]." → No Thai text in answer

=== CRITICAL REMINDERS ===

1. Only use information from Context - never add your own knowledge
2. If not in Context → Say "I cannot find this information"
3. Answer in English only (translate Thai content)
4. Every fact needs a citation at the end
5. Keep answers brief and factual

Context:
{context}

Question: {question}

Now follow STEP 1 to STEP 6. Your answer:"""


        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Question: {question}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({
                "context": context_text,
                "question": query
            })
            response = response.strip()
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "Sorry, I encountered an error while generating the answer."

if __name__ == "__main__":
    try:
        client = LLMClient()
        q = "What website security controls are required by the Thailand Web Security Standard?"
        print(f"\n--- Test Expansion ---")
        print(client.expand_query(q))
        
        print(f"\n--- Test Generation Placement ---")
        mock_docs = [Document(page_content="หน่วยงานต้องติดตั้งไฟร์วอลล์ (Firewall)", metadata={"source": "thai.pdf", "logical_page": "10"})]
        print(client.generate_answer(q, mock_docs))
        
    except Exception as e:
        print(f"Error: {e}")