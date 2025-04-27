from flask import Blueprint, request, jsonify
from app.services.evaluation_service import EvaluationService
from app.utils.nlp_evaluator import NLPEvaluator
import json

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Endpoint to evaluate LLM responses
    
    Expects JSON data in the format:
    {
        "question": "What is 5 + 3 * 2?",
        "responses": {
            "ChatGPT": "11",
            "Gemini": "10",
            "Llama": "16"
        }
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'question' not in data or 'responses' not in data:
            return jsonify({'error': 'Invalid input. Requires question and responses.'}), 400
        
        question = data['question']
        responses = data['responses']
        
        # Evaluate and save
        result = EvaluationService.evaluate_and_save(question, responses)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/evaluate/metrics', methods=['POST'])
def evaluate_metrics_only():
    """
    Endpoint to evaluate LLM responses without saving to database
    
    Expects JSON data in the format:
    {
        "question": "What is 5 + 3 * 2?",
        "responses": {
            "ChatGPT": "11",
            "Gemini": "10",
            "Llama": "16"
        }
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'question' not in data or 'responses' not in data:
            return jsonify({'error': 'Invalid input. Requires question and responses.'}), 400
        
        question = data['question']
        responses = data['responses']
        
        # Evaluate metrics for each response
        evaluation_results = {}
        for model_name, response_text in responses.items():
            evaluation_results[model_name] = NLPEvaluator.evaluate_text(question, response_text)
        
        return jsonify({
            'question': question,
            'metrics': evaluation_results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/evaluation/<int:evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """
    Endpoint to get a specific evaluation by ID
    """
    from app.models.evaluation import Evaluation
    
    try:
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
            
        return jsonify(evaluation.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 