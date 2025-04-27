from flask import Blueprint, request, jsonify
from app.services.rag_service import RAGService

rag_bp = Blueprint('rag', __name__)
rag_service = RAGService()

@rag_bp.route('/query', methods=['POST'])
def process_query():
    """
    Process a single query and return the answer with evaluation metrics.
    """
    data = request.get_json()
    if not data or 'query' not in data or 'reference' not in data:
        return jsonify({'error': 'Query and reference are required'}), 400
    
    query = data['query']
    reference = data['reference']
    
    answer, contexts, metrics = rag_service.process_query(query, reference)
    
    # Print evaluation metrics to console
    print("\nEvaluation Metrics:")
    print("------------------")
    for metric, score in metrics.items():
        print(f"{metric}: {score:.4f}")
    print("------------------\n")
    
    return jsonify({
        'answer': answer,
        'contexts': contexts,
        'evaluation_metrics': metrics
    })

@rag_bp.route('/batch', methods=['POST'])
def process_batch():
    """
    Process multiple queries and return answers with evaluation metrics.
    """
    data = request.get_json()
    if not data or 'queries' not in data or 'references' not in data:
        return jsonify({'error': 'Queries and references lists are required'}), 400
    
    queries = data['queries']
    references = data['references']
    
    if len(queries) != len(references):
        return jsonify({'error': 'Number of queries and references must match'}), 400
    
    results = rag_service.batch_process(queries, references)
    
    # Print evaluation metrics to console
    print("\nBatch Evaluation Metrics:")
    print("------------------------")
    for i, (_, _, metrics) in enumerate(results):
        print(f"\nQuery {i + 1}:")
        for metric, score in metrics.items():
            print(f"{metric}: {score:.4f}")
    print("------------------------\n")
    
    return jsonify([{
        'answer': answer,
        'contexts': contexts,
        'evaluation_metrics': metrics
    } for answer, contexts, metrics in results]) 