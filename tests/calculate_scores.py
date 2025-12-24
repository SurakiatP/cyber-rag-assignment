import json
from datetime import datetime
from pathlib import Path


INPUT_FILE = "evaluation_results.json"
OUTPUT_FILE = "evaluation_report.md"


def load_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_statistics(results):
    scores = {
        'faithfulness': [],
        'citation_accuracy': [],
        'relevance': [],
        'completeness': []
    }
    
    for result in results:
        manual = result.get('manual_scores', {})
        
        if manual.get('faithfulness') is not None:
            scores['faithfulness'].append(manual['faithfulness'])
        if manual.get('citation_accuracy') is not None:
            scores['citation_accuracy'].append(manual['citation_accuracy'])
        if manual.get('relevance') is not None:
            scores['relevance'].append(manual['relevance'])
        if manual.get('completeness') is not None:
            scores['completeness'].append(manual['completeness'])
    
    stats = {}
    for metric, values in scores.items():
        if values:
            stats[metric] = {
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        else:
            stats[metric] = {
                'average': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
    
    return stats


def calculate_by_difficulty(results):
    difficulty_groups = {}
    
    for result in results:
        diff = result.get('difficulty', 'unknown')
        if diff not in difficulty_groups:
            difficulty_groups[diff] = []
        difficulty_groups[diff].append(result)
    
    difficulty_stats = {}
    for diff, group_results in difficulty_groups.items():
        difficulty_stats[diff] = calculate_statistics(group_results)
    
    return difficulty_stats


def calculate_by_document(results):
    document_groups = {}
    
    for result in results:
        doc = result.get('document_source', 'unknown')
        if doc not in document_groups:
            document_groups[doc] = []
        document_groups[doc].append(result)
    
    document_stats = {}
    for doc, group_results in document_groups.items():
        document_stats[doc] = calculate_statistics(group_results)
    
    return document_stats


def generate_markdown_report(data, stats, diff_stats, doc_stats):
    md = []
    md.append("# RAG System Evaluation Report\n")
    
    metadata = data.get('metadata', {})
    md.append("## Metadata\n")
    md.append(f"- **Evaluation Date**: {metadata.get('evaluation_date', 'N/A')}")
    md.append(f"- **Total Queries**: {metadata.get('total_queries', 0)}")
    md.append(f"- **API URL**: {metadata.get('api_url', 'N/A')}\n")
    
    md.append("## Overall Performance\n")
    md.append("| Metric | Average | Min | Max | Count |")
    md.append("|--------|---------|-----|-----|-------|")
    
    for metric, values in stats.items():
        avg = values['average']
        if metric in ['faithfulness', 'citation_accuracy']:
            avg_str = f"{avg:.2f}%"
            min_str = f"{values['min']:.2f}%"
            max_str = f"{values['max']:.2f}%"
        else:
            avg_str = f"{avg:.2f}"
            min_str = f"{values['min']:.2f}"
            max_str = f"{values['max']:.2f}"
        
        md.append(f"| {metric.replace('_', ' ').title()} | {avg_str} | {min_str} | {max_str} | {values['count']} |")
    
    md.append("\n## Performance by Difficulty\n")
    for diff in ['easy', 'medium', 'hard']:
        if diff in diff_stats:
            md.append(f"### {diff.title()}\n")
            md.append("| Metric | Average | Count |")
            md.append("|--------|---------|-------|")
            
            for metric, values in diff_stats[diff].items():
                avg = values['average']
                if metric in ['faithfulness', 'citation_accuracy']:
                    avg_str = f"{avg:.2f}%"
                else:
                    avg_str = f"{avg:.2f}"
                md.append(f"| {metric.replace('_', ' ').title()} | {avg_str} | {values['count']} |")
            md.append("")
    
    md.append("## Performance by Document Source\n")
    for doc, doc_stat in doc_stats.items():
        md.append(f"### {doc}\n")
        md.append("| Metric | Average | Count |")
        md.append("|--------|---------|-------|")
        
        for metric, values in doc_stat.items():
            avg = values['average']
            if metric in ['faithfulness', 'citation_accuracy']:
                avg_str = f"{avg:.2f}%"
            else:
                avg_str = f"{avg:.2f}"
            md.append(f"| {metric.replace('_', ' ').title()} | {avg_str} | {values['count']} |")
        md.append("")
    
    md.append("## Detailed Results\n")
    for result in data['results']:
        md.append(f"### {result['id']}: {result['question']}\n")
        md.append(f"**Source**: {result['document_source']} | **Difficulty**: {result['difficulty']}")
        md.append(f"**Response Time**: {result['response_time_seconds']:.2f}s\n")
        
        manual = result.get('manual_scores', {})
        md.append("**Scores**:")
        md.append(f"- Faithfulness: {manual.get('faithfulness', 'N/A')}")
        md.append(f"- Citation Accuracy: {manual.get('citation_accuracy', 'N/A')}")
        md.append(f"- Relevance: {manual.get('relevance', 'N/A')}")
        md.append(f"- Completeness: {manual.get('completeness', 'N/A')}\n")
        
        citations = result.get('citations', [])
        md.append(f"**Citations**: {len(citations)} sources\n")
    
    md.append("## Recommendations\n")
    
    avg_faithfulness = stats['faithfulness']['average']
    avg_citation = stats['citation_accuracy']['average']
    avg_relevance = stats['relevance']['average']
    avg_completeness = stats['completeness']['average']
    
    if avg_faithfulness < 80:
        md.append("- **Low Faithfulness**: Review system prompt to emphasize grounding in source documents")
    if avg_citation < 85:
        md.append("- **Low Citation Accuracy**: Check citation extraction and formatting logic")
    if avg_relevance < 4.0:
        md.append("- **Low Relevance**: Improve retrieval with better query expansion or reranking")
    if avg_completeness < 3.5:
        md.append("- **Low Completeness**: Increase chunk size or improve context assembly")
    
    if all([avg_faithfulness >= 85, avg_citation >= 90, avg_relevance >= 4.0, avg_completeness >= 4.0]):
        md.append("- **Excellent Performance**: All metrics meet or exceed target thresholds")
    
    return "\n".join(md)


def generate_report():
    data = load_results(INPUT_FILE)
    results = data['results']
    
    incomplete_count = sum(1 for r in results if r['manual_scores']['faithfulness'] is None)
    
    if incomplete_count > 0:
        print(f"Warning: {incomplete_count} queries have incomplete manual scores")
        print("Please fill in all manual_scores in evaluation_results.json before generating report")
        return
    
    stats = calculate_statistics(results)
    diff_stats = calculate_by_difficulty(results)
    doc_stats = calculate_by_document(results)
    
    report = generate_markdown_report(data, stats, diff_stats, doc_stats)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report generated successfully: {OUTPUT_FILE}")
    print("\nOverall Scores:")
    print(f"  Faithfulness: {stats['faithfulness']['average']:.2f}%")
    print(f"  Citation Accuracy: {stats['citation_accuracy']['average']:.2f}%")
    print(f"  Relevance: {stats['relevance']['average']:.2f}/5")
    print(f"  Completeness: {stats['completeness']['average']:.2f}/5")


if __name__ == "__main__":
    generate_report()