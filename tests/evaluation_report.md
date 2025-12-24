# RAG System Evaluation Report

## Metadata

- **Evaluation Date**: 2025-12-24T14:55:05.729115
- **Total Queries**: 10
- **API URL**: http://localhost:8000/chat

## Overall Performance

| Metric | Average | Min | Max | Count |
|--------|---------|-----|-----|-------|
| Faithfulness | 91.20% | 80.00% | 100.00% | 10 |
| Citation Accuracy | 85.00% | 60.00% | 100.00% | 10 |
| Relevance | 4.20 | 3.00 | 5.00 | 10 |
| Completeness | 4.10 | 3.00 | 5.00 | 10 |

## Performance by Difficulty

### Easy

| Metric | Average | Count |
|--------|---------|-------|
| Faithfulness | 91.50% | 8 |
| Citation Accuracy | 85.62% | 8 |
| Relevance | 4.25 | 8 |
| Completeness | 4.12 | 8 |

### Medium

| Metric | Average | Count |
|--------|---------|-------|
| Faithfulness | 90.00% | 2 |
| Citation Accuracy | 82.50% | 2 |
| Relevance | 4.00 | 2 |
| Completeness | 4.00 | 2 |

## Performance by Document Source

### owasp-top-10.pdf

| Metric | Average | Count |
|--------|---------|-------|
| Faithfulness | 82.50% | 4 |
| Citation Accuracy | 66.25% | 4 |
| Relevance | 3.00 | 4 |
| Completeness | 3.00 | 4 |

### mitre-attack-philosophy-2020.pdf

| Metric | Average | Count |
|--------|---------|-------|
| Faithfulness | 94.00% | 3 |
| Citation Accuracy | 95.00% | 3 |
| Relevance | 5.00 | 3 |
| Completeness | 4.67 | 3 |

### thailand-web-security-standard-2025.pdf

| Metric | Average | Count |
|--------|---------|-------|
| Faithfulness | 100.00% | 3 |
| Citation Accuracy | 100.00% | 3 |
| Relevance | 5.00 | 3 |
| Completeness | 5.00 | 3 |

## Detailed Results

### Q1: What is the number one vulnerability in the OWASP Top 10: 2021 list?

**Source**: owasp-top-10.pdf | **Difficulty**: easy
**Response Time**: 145.28s

**Scores**:
- Faithfulness: 80
- Citation Accuracy: 60
- Relevance: 3
- Completeness: 3

**Citations**: 5 sources

### Q2: What does the 'Tactics' component represent in the MITRE ATT&CK framework?

**Source**: mitre-attack-philosophy-2020.pdf | **Difficulty**: easy
**Response Time**: 180.16s

**Scores**:
- Faithfulness: 95
- Citation Accuracy: 100
- Relevance: 5
- Completeness: 5

**Citations**: 5 sources

### Q3: List the 3 fundamental security characteristics mentioned in the Thailand Web Security Standard.

**Source**: thailand-web-security-standard-2025.pdf | **Difficulty**: easy
**Response Time**: 174.95s

**Scores**:
- Faithfulness: 100
- Citation Accuracy: 100
- Relevance: 5
- Completeness: 5

**Citations**: 5 sources

### Q4: Name one prevention method for 'A04:2021 - Insecure Design' from the OWASP document.

**Source**: owasp-top-10.pdf | **Difficulty**: easy
**Response Time**: 179.87s

**Scores**:
- Faithfulness: 85
- Citation Accuracy: 70
- Relevance: 3
- Completeness: 3

**Citations**: 5 sources

### Q5: According to the Thailand Web Security Standard, who constitutes the '3rd Line of Defense'?

**Source**: thailand-web-security-standard-2025.pdf | **Difficulty**: medium
**Response Time**: 175.42s

**Scores**:
- Faithfulness: 100
- Citation Accuracy: 100
- Relevance: 5
- Completeness: 5

**Citations**: 5 sources

### Q6: In MITRE ATT&CK, what are 'Sub-techniques' used for?

**Source**: mitre-attack-philosophy-2020.pdf | **Difficulty**: easy
**Response Time**: 173.84s

**Scores**:
- Faithfulness: 92
- Citation Accuracy: 95
- Relevance: 5
- Completeness: 4

**Citations**: 5 sources

### Q7: What specific log information should be recorded according to OWASP A09:2021 to help identify suspicious accounts?

**Source**: owasp-top-10.pdf | **Difficulty**: medium
**Response Time**: 192.78s

**Scores**:
- Faithfulness: 80
- Citation Accuracy: 65
- Relevance: 3
- Completeness: 3

**Citations**: 5 sources

### Q8: How often should a 'High-change Database' be backed up incrementally according to the Thailand Web Security Standard?

**Source**: thailand-web-security-standard-2025.pdf | **Difficulty**: easy
**Response Time**: 206.64s

**Scores**:
- Faithfulness: 100
- Citation Accuracy: 100
- Relevance: 5
- Completeness: 5

**Citations**: 5 sources

### Q9: List two examples of 'Security Misconfiguration' provided in OWASP A05:2021.

**Source**: owasp-top-10.pdf | **Difficulty**: easy
**Response Time**: 165.78s

**Scores**:
- Faithfulness: 85
- Citation Accuracy: 70
- Relevance: 3
- Completeness: 3

**Citations**: 5 sources

### Q10: What is the primary perspective used by the MITRE ATT&CK model?

**Source**: mitre-attack-philosophy-2020.pdf | **Difficulty**: easy
**Response Time**: 135.91s

**Scores**:
- Faithfulness: 95
- Citation Accuracy: 90
- Relevance: 5
- Completeness: 5

**Citations**: 5 sources

## Recommendations
