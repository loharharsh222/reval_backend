from flask import Blueprint, request, jsonify
from app.services.evaluation_service import EvaluationService
from app.utils.speech_recognizer import SpeechRecognizer
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

@evaluation_bp.route('/evaluate/audio', methods=['POST'])
def evaluate_audio():
    """
    Endpoint to evaluate LLM responses from audio input
    
    Expects multipart form data with:
    - audio: Audio file containing the spoken question
    - responses: JSON string of model responses
    """
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        # Get the audio file
        audio_file = request.files['audio']
        
        # Check if responses are in the request
        if 'responses' not in request.form:
            return jsonify({'error': 'No responses provided'}), 400
            
        # Get responses
        responses = request.form['responses']
        
        # Convert audio to text
        question = SpeechRecognizer.recognize_from_bytes(audio_file.read())
        
        # If speech recognition failed
        if question.startswith("Error") or question.startswith("Speech recognition could not"):
            return jsonify({'error': question}), 400
            
        # Parse responses JSON
        try:
            responses = json.loads(responses)
        except:
            return jsonify({'error': 'Invalid responses JSON'}), 400
            
        # Evaluate and save
        result = EvaluationService.evaluate_and_save(question, responses)
        
        return jsonify(result), 200
        
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