# Cybersecurity RAG Assistant

A production-grade Retrieval-Augmented Generation (RAG) system designed to answer cybersecurity questions using only provided dataset documents. Built with hybrid search, multilingual support (Thai/English), and strict grounding enforcement to prevent hallucinations.

## Project Overview

This system implements a local RAG pipeline that processes three cybersecurity standards documents:
- OWASP Top 10
- Thailand Web Security Standard (2025)
- MITRE ATT&CK Design & Philosophy (2020)

The system uses advanced document processing including OCR for Thai language PDFs, hybrid retrieval combining keyword and semantic search, and cross-encoder reranking to provide accurate, citation-backed answers.

## Core Capabilities

As required by the assignment, this system:

1. **Dataset-Only Grounding**: All answers are strictly derived from the three provided documents. No external knowledge or hallucinations are permitted.

2. **Citation Enforcement**: Every answer includes clear citations in the format `[Source: filename.pdf, Page: X]` to enable verification.

3. **Multilingual Processing**: 
   - Processes Thai language PDFs using OCR and text normalization
   - Handles bilingual queries (Thai/English)
   - Generates answers in English with proper translation

4. **Hybrid Retrieval**: Combines BM25 keyword search and semantic vector search for optimal retrieval accuracy.

5. **Reranking Pipeline**: Uses cross-encoder reranking to refine top-20 candidates down to top-7 most relevant contexts.

6. **Fallback Strategy**: Responds with "I cannot find this information in the provided documents" when answers are not available in the dataset.

## Project Structure

```
cyber-rag-assignment/
│
├── dataset/                   # Input PDF documents
│   ├── thailand-web-security-standard-2025.pdf
│   ├── owasp-top-10.pdf
│   └── mitre-attack-philosophy-2020.pdf
│
├── database/                  # Persisted indexes (auto-generated)
│   ├── faiss_index/           # Vector store (BAAI/bge-m3)
│   └── bm25_retriever.pkl     # Keyword index
│
├── output/                    # Processing artifacts
│   └── ingested_documents.json
│
├── src/                       # Core implementation
│   ├── document_processor.py  # PDF ingestion (OCR + Layout Analysis)
│   ├── rag_engine.py          # Hybrid search + Reranking
│   └── llm_client.py          # LLM prompting + Answer generation
│
├── tests/                     # Test suite
│   └── test_reference_samples.py
│
├── app.py                     # FastAPI entry point
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # App container definition
├── requirements.txt           # Python dependencies
├── .env.example               # Configuration template
│
├── README.md                  # This file
├── ARCHITECTURE.md            # System design documentation
└── EVALUATION.md              # Test results and analysis
```

## Documentation

For detailed technical information, please refer to:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, pipeline explanation, and technical decisions
- **[EVALUATION.md](EVALUATION.md)** - Test results, sample Q&A, and grounding validation

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Quick Start

**Step 1: Clone and Navigate**
```bash
git clone https://github.com/SurakiatP/cyber-rag-assignment.git
cd cyber-rag-assignment
```

**Step 2: Copy Environment Configuration**
```bash
cp .env.example .env
```

**Step 3: Start Docker Services**
```bash
docker-compose up -d
```

This will automatically:
- Download Ollama and pull Gemma 3:4b model (~2GB, 3-5 minutes)
- Build the RAG API container
- Process documents and create indexes (~6-8 minutes on first run)

**Step 4: Monitor Startup Progress**
```bash
docker-compose logs -f rag-api
```

Wait until you see:
```
INFO: Database loaded successfully.
INFO: Application startup complete.
```

Press `Ctrl+C` to exit logs (services continue running in background).

**Step 5: Access Interactive API Documentation**

Open your browser and navigate to:
```
http://localhost:8000/docs
```

**Step 6: Test the System**

In the Swagger UI:
1. Click on **POST /chat** endpoint
2. Click **"Try it out"** button
3. Replace the example with:
```json
{
  "question": "What is the difference between a Tactic and a Technique in MITRE ATT&CK?"
}
```
4. Click **"Execute"**
5. View the response with citation

Expected response format:
```json
{
  "answer": "Tactics represent the ‘why’ of an ATT&amp;CK technique or sub-technique. It is the adversary’s tactical objective: the reason for performing an action [Source: mitre-attack-philosophy-2020.pdf, Page: 8b]. Techniques, on the other hand, describe the means by which adversaries achieve tactical goals [Source: mitre-attack-philosophy-2020.pdf, Page: 1b].  Essentially, tactics are the goals, and techniques are the methods to achieve those goals [Source: mitre-attack-philosophy-2020.pdf, Page: 9b].",
  "expanded_query": "What is the difference between a Tactic and a Technique in MITRE ATT&CK? การแทรกซึม, Tactic, Technique, MITRE ATT&CK, tactic, technique, attack techniques, MITRE ATT&CK framework",
  "retrieved_docs": [
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "8b",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "1b",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "6b",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "25b",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "1b",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "3a",
      "score": "N/A"
    },
    {
      "source": "mitre-attack-philosophy-2020.pdf",
      "page": "9b",
      "score": "N/A"
    }
  ],
  "processing_time": 435.9
}
```

### Alternative: Command Line Testing

If you prefer using curl instead of the browser:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the difference between a Tactic and a Technique in MITRE ATT&CK?"}'
```

### Useful Docker Commands

**View logs:**
```bash
docker-compose logs -f rag-api
```

**Stop the system:**
```bash
docker-compose down
```

**Restart after code changes:**
```bash
docker-compose down
docker-compose up -d --build
```

### Running Tests

```bash
# Inside the container
docker exec cyber-rag-app python -m pytest tests/test_reference_samples.py -v

# Or run locally if dependencies installed
python -m pytest tests/test_reference_samples.py -v
```

Expected output:
```
test_q1_owasp_broken_access_control PASSED
test_q2_thai_web_security PASSED
test_q3_mitre_tactic_vs_technique PASSED
test_q4_owasp_injection_mitigation PASSED
test_q5_mitre_persistence PASSED

===== 5 passed in 42.3s =====
```

## Configuration

Key environment variables in `.env`:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL_NAME=gemma3:4b
LLM_TEMPERATURE=0.2

# Embedding & Retrieval
EMBEDDING_MODEL_NAME=BAAI/bge-m3
RERANKER_MODEL_NAME=BAAI/bge-reranker-v2-m3

# Chunking Strategy
CHUNK_SIZE=1100
CHUNK_OVERLAP=200

# Retrieval Pipeline
RETRIEVAL_K=20
RERANK_TOP_N=7
```

## Troubleshooting

**Issue: Container fails to start**
```bash
# Check logs
docker-compose logs rag-api

# Common fix: Insufficient memory
# Increase Docker memory limit to 8GB+
```

**Issue: Ollama model not found**
```bash
# Manually pull model
docker exec cyber-rag-ollama ollama pull gemma3:4b
```

**Issue: Index not found**
```bash
# Trigger rebuild
curl -X POST http://localhost:8000/rebuild-index

# Or restart with fresh data
docker-compose down
rm -rf database/ output/
docker-compose up -d
```

## Tech Stack Summary

- **Framework**: FastAPI (API), LangChain (Orchestration)
- **LLM**: Gemma 3:4b via Ollama (local inference)
- **Embeddings**: BAAI/bge-m3 (multilingual, 1024-dim)
- **Reranker**: BAAI/bge-reranker-v2-m3 (cross-encoder)
- **Vector Store**: FAISS (exact search with IndexFlat)
- **Keyword Search**: BM25 with PyThaiNLP tokenization
- **OCR**: EasyOCR + Docling (Thai language support)
- **Deployment**: Docker Compose

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8GB | 16GB |
| CPU | 4 cores | 8 cores |
| Disk | 10GB | 20GB |
| GPU | Not required | Optional (3-5x speedup) |

## Performance Characteristics

- **Indexing Time**: 6-8 minutes (one-time, on first run)
- **Query Latency**: 7-10 seconds per query (CPU)
- **Model Memory**: ~4GB RAM (Gemma 3:4b + embeddings + reranker)
- **Index Size**: ~50MB (for 3 documents, ~150 pages)

## Author

**Surakiat Kansa-ard (Park)**
- GitHub: [SurakiatP](https://github.com/SurakiatP)
- LinkedIn: [surakiat-kansa-ard](https://www.linkedin.com/in/surakiat-kansa-ard-171942351/)

## Assignment Compliance

This project fulfills all requirements specified in the assignment:

1. Uses only the three provided documents in `dataset/`
2. Implements complete RAG pipeline (load → chunk → embed → retrieve → generate)
3. Includes clear citations referencing source files and pages
4. Provides architecture explanation and system diagram
5. Includes evaluation examples with test results
6. Delivers clean, readable, and well-organized source code
7. Includes comprehensive documentation (README, ARCHITECTURE, EVALUATION)

For grading rubric alignment:
- **Answer Grounding & Dataset Compliance (35%)**: See [EVALUATION.md](EVALUATION.md)
- **System Design & Architecture (25%)**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Code Quality & Maintainability (20%)**: See `src/` directory
- **Communication & Documentation (15%)**: This README and related docs
- **Bonus Points**: Hybrid search, reranking, Thai OCR, cross-encoder reranker

## License

This project is submitted as part of an AI Engineering assessment for DATAFARM.
