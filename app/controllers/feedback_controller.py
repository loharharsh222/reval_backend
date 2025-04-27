from flask import Blueprint, request, jsonify
from app.services.feedback_service import FeedbackService
from app.models.leaderboard import Leaderboard
from app import db

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
def add_feedback():
    """
    Endpoint to add user feedback with ratings
    
    Expects JSON data in the format:
    {
        "feedback": {
            "ChatGPT": 3,
            "Gemini": 4,
            "Llama": 3
        },
        "scores": {
            "ChatGPT": { ... metrics ... },
            "Gemini": { ... metrics ... },
            "Llama": { ... metrics ... }
        }
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'feedback' not in data:
            return jsonify({'error': 'Invalid input. Requires feedback ratings.'}), 400
        
        feedback = data['feedback']
        
        # Update ratings for each model
        for model_name, rating in feedback.items():
            # Validate rating (should be 1-5)
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return jsonify({'error': f'Invalid rating for {model_name}. Must be between 1 and 5.'}), 400
            
            # Get the model from leaderboard
            model = Leaderboard.query.filter_by(model_name=model_name).first()
            if not model:
                # Create a new model entry if it doesn't exist
                model = Leaderboard(model_name=model_name)
                db.session.add(model)
            
            # Update the rating
            model.update_user_rating(rating)
        
        db.session.commit()
        
        # Calculate and return ranking
        ranks = calculate_model_ranking()
        
        return jsonify({
            'message': 'Feedback saved successfully',
            'ranking': ranks
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/ranking', methods=['GET'])
def get_ranking():
    """
    Endpoint to get current model ranking based on metrics and user feedback
    """
    try:
        # Calculate and return ranking
        ranks = calculate_model_ranking()
        
        return jsonify(ranks), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_model_ranking():
    """
    Calculate model ranking based on metrics and user feedback
    
    Returns:
        List of models with their rank and scores
    """
    # Get all models from leaderboard
    models = Leaderboard.query.all()
    
    # Calculate combined score for each model
    ranking_data = []
    for model in models:
        # Skip models with no evaluations
        if model.total_evaluations == 0:
            continue
            
        # Calculate combined score (50% metrics, 50% user feedback)
        nlp_score = model.avg_final_score
        
        # If no user feedback yet, use only NLP score
        if model.feedback_count == 0:
            combined_score = nlp_score
        else:
            # Normalize user rating to 0-1 range (from 1-5)
            user_score = (model.user_rating - 1) / 4
            combined_score = 0.5 * nlp_score + 0.5 * user_score
        
        ranking_data.append({
            'model': model.model_name,
            'combined_score': round(combined_score, 2),
            'nlp_score': round(nlp_score, 2),
            'user_rating': model.user_rating if model.feedback_count > 0 else None,
            'feedback_count': model.feedback_count,
            'evaluation_count': model.total_evaluations
        })
    
    # Sort by combined score (descending)
    ranking_data.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Add ranks
    for i, item in enumerate(ranking_data):
        item['rank'] = i + 1
    
    return ranking_data 