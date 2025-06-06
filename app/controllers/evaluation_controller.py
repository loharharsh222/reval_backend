from flask import Blueprint, request, jsonify
from app.services.evaluation_service import EvaluationService
from app.utils.nlp_evaluator import NLPEvaluator
import json

evaluation_bp = Blueprint('evaluation', __name__)

def _validate_and_sanitize_responses(responses):
    """Helper function to validate and sanitize responses"""
    invalid_responses = []
    
    for model, resp in list(responses.items()):
        # Check for [object Object] or [object Response] patterns
        if isinstance(resp, str) and (resp.strip() == '[object Object]' or 
                                     resp.strip() == '[object Response]' or
                                     resp.startswith('[object ')):
            invalid_responses.append(model)
            
        # Try to extract text from JSON responses
        elif isinstance(resp, str) and (resp.startswith('{') and resp.endswith('}')):
            try:
                json_data = json.loads(resp)
                if isinstance(json_data, dict) and 'text' in json_data:
                    extracted_text = json_data['text']
                    print(f"  INFO: Extracted text from JSON for {model}: '{extracted_text[:50]}{'...' if len(extracted_text) > 50 else ''}'")
                    responses[model] = extracted_text
                elif not json_data:
                    print(f"  WARNING: Empty JSON response from {model}")
                    responses[model] = "Empty response"
            except json.JSONDecodeError:
                print(f"  WARNING: Failed to parse JSON for {model}, using raw string")
    
    return invalid_responses

def _debug_input_data(question, responses, endpoint_name="API"):
    """Helper function for debug logging"""
    print(f"\n{'*'*80}")
    print(f"DEBUG - {endpoint_name} INPUT DATA:")
    print(f"Question: {question}")
    print("Responses:")
    for model, resp in responses.items():
        print(f"- {model}: '{resp[:50]}{'...' if len(resp) > 50 else ''}'")

@evaluation_bp.route('/evaluate', methods=['POST'])
def evaluate():
    """Endpoint to evaluate LLM responses and save to database"""
    try:
        data = request.json
        
        if not data or 'question' not in data or 'responses' not in data:
            return jsonify({'error': 'Invalid input. Requires question and responses.'}), 400
        
        question = data['question']
        responses = data['responses']
        
        _debug_input_data(question, responses)
        
        invalid_responses = _validate_and_sanitize_responses(responses)
        
        if invalid_responses:
            error_msg = f"Invalid response format detected for models: {', '.join(invalid_responses)}"
            return jsonify({
                'error': error_msg,
                'help': "Make sure to extract the text content from response objects before sending."
            }), 400
        
        unique_responses = set(responses.values())
        if len(unique_responses) < len(responses):
            print("WARNING: Some model responses are identical!")
        print("*"*80 + "\n")
        
        result = EvaluationService.evaluate_and_save(question, responses)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/evaluate/metrics', methods=['POST'])
def evaluate_metrics_only():
    """Endpoint to evaluate LLM responses without saving to database"""
    try:
        data = request.json
        
        if not data or 'question' not in data or 'responses' not in data:
            return jsonify({'error': 'Invalid input. Requires question and responses.'}), 400
        
        question = data['question']
        responses = data['responses']
        
        _debug_input_data(question, responses, "METRICS")
        
        invalid_responses = _validate_and_sanitize_responses(responses)
        
        if invalid_responses:
            error_msg = f"Invalid response format detected for models: {', '.join(invalid_responses)}"
            return jsonify({
                'error': error_msg,
                'help': "Make sure to extract the text content from response objects before sending."
            }), 400
        
        unique_responses = set(responses.values())
        if len(unique_responses) < len(responses):
            print("WARNING: Some model responses are identical!")
        print("*"*80 + "\n")
        
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
    """Endpoint to get a specific evaluation by ID"""
    from app.models.evaluation import Evaluation
    
    try:
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
            
        return jsonify(evaluation.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500