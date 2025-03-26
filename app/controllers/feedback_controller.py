from flask import Blueprint, request, jsonify
from app.services.feedback_service import FeedbackService

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
def add_feedback():
    """
    Endpoint to add user feedback (upvote/downvote)
    
    Expects JSON data in the format:
    {
        "evaluation_id": 1,
        "model_name": "ChatGPT",
        "vote_type": "upvote"  # or "downvote"
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'evaluation_id' not in data or 'model_name' not in data or 'vote_type' not in data:
            return jsonify({'error': 'Invalid input. Requires evaluation_id, model_name, and vote_type.'}), 400
        
        # Get input data
        evaluation_id = data['evaluation_id']
        model_name = data['model_name']
        vote_type = data['vote_type']
        
        # Validate vote type
        if vote_type not in ['upvote', 'downvote']:
            return jsonify({'error': 'Invalid vote_type. Must be "upvote" or "downvote".'}), 400
        
        # Save feedback
        feedback = FeedbackService.save_feedback(evaluation_id, model_name, vote_type)
        
        return jsonify({
            'message': f'Feedback ({vote_type}) saved for {model_name}',
            'feedback_id': feedback.id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """
    Endpoint to get feedback statistics
    
    Optional query parameters:
    - evaluation_id: Filter by evaluation ID
    - model_name: Filter by model name
    """
    try:
        # Get query parameters
        evaluation_id = request.args.get('evaluation_id', type=int)
        model_name = request.args.get('model_name')
        
        # Get feedback stats
        stats = FeedbackService.get_feedback_stats(evaluation_id, model_name)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 