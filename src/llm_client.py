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
        self.generate_model_name = os.getenv("LLM_GENERATE_MODEL_NAME", "llama3.1:8b")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        timeout = float(os.getenv("LLM_TIMEOUT", "120.0"))
        
        
        logger.info(f"Initializing Expander LLM: {self.expand_model_name}")
        self.llm_expand = ChatOllama(
            model=self.expand_model_name,
            base_url=base_url,
            temperature=temperature,
            keep_alive="1h",
            num_predict=512,
            request_timeout=timeout
        )

        logger.info(f"Initializing Generator LLM: {self.generate_model_name}")
        self.llm_generate = ChatOllama(
            model=self.generate_model_name,
            base_url=base_url,
            temperature=temperature,
            keep_alive="1h",
            num_predict=512,
            request_timeout=timeout
        )

    def expand_query(self, query: str) -> str:
        logger.info(f"Expanding query: '{query}'")
        
        system_prompt = """You are a Bilingual Search Query Optimizer.
Your goal is to convert the user's query into a single string of space-separated keywords, prioritizing Thai translation followed by English technical terms.

=== INSTRUCTIONS ===

1. **Analyze**: Understand the core technical concepts of the query.
2. **Translate to Thai**: 
   - Translate the main concepts into Thai.
   - Use both formal terms (e.g., "การโจมตีแบบปฏิเสธการให้บริการ") and common terms (e.g., "ยิงเซิร์ฟเวอร์").
3. **Extract English Keywords**:
   - Keep the original English technical terms.
   - Add relevant acronyms (e.g., "DDoS") or standard synonyms.
4. **Format**:
   - Output **Thai Keywords first**, followed by **English Keywords**.
   - Use **ONLY SPACES** as separators.
   - **NO COMMAS**, NO pipes (|), NO special characters.
   - **NO** explanations.

=== OUTPUT FORMAT ===
<Thai Keyword 1> <Thai Keyword 2> <Thai Keyword 3> <English Keyword 1> <English Keyword 2> <English Keyword 3>

=== EXAMPLES ===

Query: "How to prevent SQL Injection?"
Output: การป้องกันการโจมตีฐานข้อมูล ช่องโหว่ความปลอดภัย การตรวจสอบข้อมูลนำเข้า SQL Injection Prevention Database Security Input Validation

Query: "log retention requirements"
Output: ข้อกำหนดการจัดเก็บข้อมูลจราจร ระยะเวลาเก็บข้อมูลจราจร พ.ร.บ.คอมพิวเตอร์ Log Retention Policy Compliance Audit Logs 90 days

Query: "What is Cross-Site Scripting?"
Output: การโจมตีแบบข้ามไซต์ สคริปต์ข้ามไซต์ ช่องโหว่หน้าเว็บ Cross-Site Scripting XSS Web Vulnerability

Now process this query:"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm_expand | StrOutputParser()
        
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

        system_prompt = """You are a Senior Cybersecurity Auditor and Compliance Specialist.
Your task is to answer user questions based **EXCLUSIVELY** on the provided Context.

=== STRICT GUIDELINES ===

1. **NO OUTSIDE KNOWLEDGE**: You must act as if you know NOTHING about cybersecurity other than what is written in the Context.
2. **EVIDENCE-BASED**: Every single claim you make must be supported by a specific sentence in the Context.
3. **LANGUAGE**: 
   - Analyze documents in both Thai and English.
   - **Output your final answer in ENGLISH ONLY.**
   - Translate Thai concepts accurately to English technical terms.

=== CITATION RULES (CRITICAL) ===

- You MUST cite the source for every statement.
- Format: `[Source: filename, Page: X]`
- Place citations immediately after the sentence/phrase they support.
- If multiple documents support a fact, list them all: `[Source: doc1.pdf, Page: 5; Source: doc2.pdf, Page: 8]`
- **DO NOT** create a "References" section at the end. Citations must be inline.

=== REASONING PROCESS ===

1. Scan the Context for keywords related to: "{question}"
2. If the Context contains conflicting information (e.g., Doc A says "Block port 80" but Doc B says "Allow port 80"), mention the conflict explicitly.
3. If the Context does **NOT** contain the answer, reply exactly:
   "I cannot find this information in the provided documents."

=== RESPONSE STRUCTURE ===

- **Direct Answer**: Start with a direct answer to the question.
- **Key Details**: Use bullet points for readability.
- **Conciseness**: Keep it professional and to the point.

=== EXAMPLES (RESPONSE Follow these patterns) ===

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
Answer: I cannot find this information in the provided documents.

Example 4: Combining Facts
Context:
--- Document 1 (Source: network.pdf, Page: 3) ---
The DMZ isolates external services.
--- Document 2 (Source: admin_guide.pdf, Page: 10) ---
Web servers must be placed in the DMZ.

Question: Where should web servers be placed and why?
Answer: Web servers must be located in the DMZ [Source: admin_guide.pdf, Page: 10]. This is done to isolate external services from the internal network [Source: network.pdf, Page: 3].

=== END OF EXAMPLES ===

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