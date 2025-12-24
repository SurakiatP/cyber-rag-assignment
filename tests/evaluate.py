import json
import requests
from datetime import datetime
from pathlib import Path


API_URL = "http://localhost:8000/chat"

TEST_QUERIES_FILE = "test_queries.json"
OUTPUT_FILE = "evaluation_results.json"


def load_test_queries(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['queries']


def query_rag_api(question):
    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying API: {e}")
        return None


def extract_citations(response_data):
    if not response_data:
        return []
    
    citations = []
    retrieved_docs = response_data.get('retrieved_docs', [])
    
    for doc in retrieved_docs:
        citations.append({
            'document': doc.get('source', 'Unknown'),
            'page': doc.get('page', 'N/A'),
            'score': doc.get('score', 'N/A')
        })
    
    return citations


def run_evaluation():
    all_queries = load_test_queries(TEST_QUERIES_FILE)
    queries = all_queries[:10]  # Limit to first 10 queries for faster evaluation
    results = []
    
    print(f"Starting evaluation with {len(queries)} queries (limited from {len(all_queries)} total)...")
    print("Note: Each query may take 1-3 minutes due to query expansion and generation\n")
    
    for i, query_obj in enumerate(queries, 1):
        print(f"Processing {i}/{len(queries)}: {query_obj['id']} - {query_obj['question'][:60]}...")
        
        import time
        start = time.time()
        response = query_rag_api(query_obj['question'])
        elapsed = time.time() - start
        
        if response:
            answer_text = response.get('answer', '')
            citations = extract_citations(response)
            response_time = response.get('processing_time', 0)
            print(f"  ✓ Completed in {elapsed:.1f}s")
        else:
            answer_text = "API Error"
            citations = []
            response_time = 0
            print(f"  ✗ Failed after {elapsed:.1f}s")
        
        result = {
            'id': query_obj['id'],
            'question': query_obj['question'],
            'document_source': query_obj['document_source'],
            'query_type': query_obj['query_type'],
            'expected_topics': query_obj['expected_topics'],
            'difficulty': query_obj['difficulty'],
            'response': answer_text,
            'citations': citations,
            'response_time_seconds': response_time,
            'manual_scores': {
                'faithfulness': None,
                'citation_accuracy': None,
                'relevance': None,
                'completeness': None
            }
        }
        
        results.append(result)
    
    output = {
        'metadata': {
            'evaluation_date': datetime.now().isoformat(),
            'total_queries': len(queries),
            'api_url': API_URL
        },
        'results': results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nEvaluation complete. Results saved to {OUTPUT_FILE}")
    print("Next step: Fill in manual_scores for each result")


if __name__ == "__main__":
    run_evaluation()