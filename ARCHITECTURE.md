# System Architecture

This document explains the RAG system design, technical workflow, and key architectural decisions.

## System Architecture Diagram

![System Architecture](IMAGE_README/system_architecture.png)

The architecture consists of three stages: Ingestion (document processing), Indexing (database creation), and Retrieval & Generation (query handling).

## Pipeline Workflow

### Stage 1: Ingestion

Documents are processed using two specialized pipelines:

**Thai Document Pipeline (thailand-web-security-standard-2025.pdf):**
1. Rasterize PDF pages to images at 3x scale (216 DPI) using pypdfium2
2. Preprocess images with grayscale conversion and autocontrast (Pillow)
3. Extract text via EasyOCR with Thai/English language support
4. Analyze layout structure using Docling (headers, paragraphs, tables)
5. Normalize Thai text with PyThaiNLP (standardize vowels, tone marks)

**English Document Pipeline (owasp-top-10.pdf, mitre-attack-philosophy-2020.pdf):**
1. Extract native PDF text using Docling
2. Map physical page numbers to logical page numbers (e.g., PDF page 15 → "12b")
3. Export to Markdown format preserving document structure

**Why Thai OCR?** Thai PDFs often have encoding issues causing copy-paste corruption. Converting to images and using OCR guarantees accurate text extraction regardless of PDF quality.

**Why Logical Page Mapping?** Ensures citations reference the correct printed page numbers that users see when opening PDFs, improving answer verifiability.

### Stage 2: Indexing

**Chunking Strategy:**
- Size: 1100 characters per chunk (~275-550 tokens)
- Overlap: 200 characters
- Rationale: Balances complete concept capture with retrieval precision. The 200-char overlap prevents technical terms from being split at boundaries while optimizing query speed.

**Dual Indexing:**
- **Vector Index**: BAAI/bge-m3 embeddings (1024-dim, multilingual) stored in FAISS IndexFlat
- **Keyword Index**: BM25 with PyThaiNLP word tokenization for Thai language support

### Stage 3: Retrieval & Generation

**Query Processing Flow:**
1. **Expansion**: Gemma 3:4b generates bilingual keywords (Thai + English) from user query
2. **Hybrid Search**: Combines BM25 (40% weight) and vector search (60% weight) to retrieve top-20 candidates
3. **Reranking**: Cross-encoder (BAAI/bge-reranker-v2-m3) refines top-20 down to top-7 most relevant chunks
4. **Generation**: Gemma 3:4b produces answer with mandatory citations using top-7 contexts

**Query Expansion Example:**
```
Input: "What is log retention?"
Output: "What is log retention? การเก็บ log, log storage, retention period, การจัดเก็บบันทึก"
```

## Key Design Decisions

### Why Hybrid Search?

| Component | Strength | Example |
|-----------|----------|---------|
| BM25 (40%) | Exact matches, acronyms | "OWASP", "MFA", "SQL injection" |
| Vector (60%) | Semantic similarity | "authentication" ≈ "identity verification" |

Cybersecurity documents contain both precise technical terms requiring exact matching and concepts needing semantic understanding. Hybrid search achieves both objectives.

### Why Two-Stage Retrieval?

**Stage 1 - Bi-Encoder (Top 20):** Fast retrieval for high recall  
**Stage 2 - Cross-Encoder (Top 7):** Accurate reranking for high precision

Cross-encoders are more accurate but slower. Using them only for final refinement of 20 candidates balances speed and quality.

### Why Gemma 3:4b?

**Selection Criteria:**
- **Size**: 4B parameters run efficiently on CPU (3-5s inference)
- **Multilingual**: Handles Thai/English keyword generation and translation
- **Context Window**: 8K tokens fits 7 chunks plus system prompts
- **Instruction Following**: Strong adherence to structured citation format

Alternative models (Llama 3.1 8B, Qwen 2.5 7B) offer higher accuracy but are 2-3x slower on CPU, making Gemma 3:4b optimal for this deployment.

### Why BAAI/bge-m3 Embeddings?

- Native support for 100+ languages including Thai
- Handles up to 8192 token sequences (entire document chunks)
- Top-ranked on MTEB multilingual benchmarks
- Same model family as reranker for semantic consistency

### Why This Tech Stack?

**Core Framework:**
- **FastAPI**: Async API with automatic Swagger documentation
- **LangChain**: Pre-built RAG components and orchestration
- **Ollama**: Local LLM inference without API costs

**Search Components:**
- **FAISS IndexFlat**: Exact search for small datasets (<1K docs)
- **BM25 + PyThaiNLP**: Thai-aware keyword matching
- **Cross-Encoder Reranker**: Production-grade precision refinement

**Deployment:**
- **Docker Compose**: Reproducible multi-container setup
- **Volume Persistence**: Indexes and models survive restarts

### Why Low Temperature (0.2)?

Temperature 0.2 provides deterministic, factual responses without being rigidly robotic. Higher temperatures (>0.5) risk hallucination; lower temperatures (0.0) produce unnatural phrasing.

## Performance Characteristics

**Query Latency (CPU):** 7-10 seconds average

| Stage | Time | Percentage |
|-------|------|------------|
| Query Expansion | 1.2s | 15% |
| Hybrid Retrieval | 0.3s | 4% |
| Reranking | 2.5s | 31% |
| Answer Generation | 4.1s | 50% |

**With GPU (optional):** Total latency reduces to 4-6 seconds (3-5x speedup on reranking and generation).

**Indexing (one-time):** 6-8 minutes for all three documents.

## Trade-offs

**Strengths:**
- Strict grounding prevents hallucination
- Multilingual support handles Thai content
- Hybrid approach maximizes retrieval accuracy
- Local deployment ensures data privacy

**Limitations:**
- CPU-only deployment prioritizes portability over speed
- Conservative fallback may refuse ambiguous but valid questions
- Optimized for small datasets (<1000 documents)

**Scalability:** For datasets >10K documents, switch to FAISS IVF index and increase retrieval K to maintain recall.

## Conclusion

This architecture prioritizes answer accuracy and verifiability. The combination of hybrid retrieval, two-stage reranking, and strict prompt engineering ensures all responses are grounded in the dataset with clear citations. The system successfully handles multilingual content while maintaining production-quality precision through careful engineering of each pipeline stage.