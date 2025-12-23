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
        self.expand_model_name = os.getenv("LLM_EXPAND_MODEL_NAME", "scb10x/typhoon2.1-gemma3-4b:latest")
        self.generate_model_name = os.getenv("LLM_GENERATE_MODEL_NAME", "qwen2.5:7b-instruct-q4_0")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        timeout = float(os.getenv("LLM_TIMEOUT", "120.0"))
        
        
        logger.info(f"Initializing Expander LLM: {self.expand_model_name}")
        self.llm_expand = ChatOllama(
            model=self.expand_model_name,
            base_url=base_url,
            temperature=temperature,
            keep_alive="1h",
            num_predict=100,
            request_timeout=timeout
        )

        logger.info(f"Initializing Generator LLM: {self.generate_model_name}")
        self.llm_generate = ChatOllama(
            model=self.generate_model_name,
            base_url=base_url,
            temperature=temperature,
            keep_alive="1h",
            num_predict=350,
            request_timeout=timeout
        )

    def expand_query(self, query: str) -> str:
        logger.info(f"Expanding query: '{query}'")
        
        system_prompt = """You are a Bilingual Search Query Optimizer for Thai-English cybersecurity queries.

TASK: Convert user queries into alternating Thai-English keyword pairs for hybrid search.

RULES:
1. Extract 2-6 core concepts from the query
2. For each concept, provide:
   - Thai translation (formal + colloquial terms)
   - English technical term or acronym (eg. OWASP, MITRE ATT&CK, ...)
3. Output format: <Thai1> <English1> <Thai2> <English2> [<Thai3> <English3>]
4. Use ONLY spaces as separators (no commas, pipes, or special characters)
5. **OUTPUT KEYWORDS ONLY** - NO explanations, NO reasoning, NO query repetition

EXAMPLES:

Input: "How to prevent SQL Injection?"
Output: การป้องกันการโจมตีฐานข้อมูล SQL ช่องโหว่ความปลอดภัย Injection การป้องกัน Prevention

Input: "log retention requirements"
Output: ข้อกำหนดการจัดเก็บล็อก Log ระยะเวลาเก็บข้อมูล Retention ข้อกำหนดตามกฎหมาย Compliance

Input: "What is Cross-Site Scripting?"
Output: การโจมตีแบบข้ามไซต์ Cross-Site ช่องโหว่ XSS Scripting

Query:"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm_expand | StrOutputParser()
        
        try:
            keywords = chain.invoke({"query": query})
            keywords = keywords.replace('\n', ' ').replace('"', '').replace('Output: ','') .strip()
            keywords = re.sub(r'(Here is|The translation|However).*', '', keywords, flags=re.IGNORECASE)
            # query = keywords.replace('?', '').strip()

            # expanded_query = f"{query} {keywords}"
            expanded_query = f"{keywords}"
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

        system_prompt = """You are a Cybersecurity Compliance Specialist answering questions using ONLY the provided Context.

CORE RULES:
1. Base answers EXCLUSIVELY on Context - ignore all outside knowledge
2. Cite every claim immediately: [Source: filename, Page: X]
3. Output in ENGLISH only (translate Thai terms to English)
4. If answer not in Context, respond: "I cannot find this information in the provided documents."

CITATION FORMAT:
- Inline only - no reference sections
- Single source: [Source: policy.pdf, Page: 5]
- Multiple sources: [Source: doc1.pdf, Page: 3; Source: doc2.pdf, Page: 7]
- Note conflicts explicitly when documents disagree

RESPONSE STRUCTURE:
- Direct answer first
- Support with bullet points if needed
- Keep concise and professional

EXAMPLES:

Example 1: Single Source (Thai to English)
Context:
--- Document 1 (Source: policy_th.pdf, Page: 12) ---
รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร และต้องประกอบด้วยตัวเลขและอักษรพิเศษ

Question: What are the password complexity requirements?
Answer: Passwords must be at least 8 characters long and contain both numbers and special characters [Source: policy_th.pdf, Page: 12].

Example 2: Multiple Sources & Conflict
Context:
--- Document 1 (Source: old_standard.pdf, Page: 5) ---
Data retention period is 90 days.
--- Document 2 (Source: new_reg_2024.pdf, Page: 2) ---
All logs must be retained for at least 1 year.

Question: How long should logs be kept?
Answer: There is conflicting information in the provided documents. One document states the retention period is 90 days [Source: old_standard.pdf, Page: 5], while a newer regulation requires logs to be retained for at least 1 year [Source: new_reg_2024.pdf, Page: 2].

Example 3: Insufficient Information
Context:
--- Document 1 (Source: firewall_config.pdf, Page: 1) ---
Port 80 and 443 should be open for web traffic.

Question: How do I configure the backup server?
Answer: I cannot find this information in the provided documents. **In this case, there's no need to enter a source files**

Context:
{context}

Question: {question}

Answer:"""


        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Question: {question}")
        ])

        chain = prompt | self.llm_generate | StrOutputParser()

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