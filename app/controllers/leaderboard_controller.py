from flask import Blueprint, request, jsonify
from app.services.leaderboard_service import LeaderboardService

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Endpoint to get the current leaderboard
    
    Optional query parameters:
    - limit: Maximum number of entries to return (default: 10)
    """
    try:
        # Get the limit parameter
        limit = request.args.get('limit', default=10, type=int)
        
        # Get the leaderboard
        leaderboard = LeaderboardService.get_leaderboard(limit)
        
        return jsonify(leaderboard), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/leaderboard/model/<model_name>', methods=['GET'])
def get_model_metrics(model_name):
    """
    Endpoint to get detailed metrics for a specific model
    """
    try:
        # Get model metrics
        metrics = LeaderboardService.get_model_metrics(model_name)
        
        if not metrics:
            return jsonify({'error': f'Model "{model_name}" not found'}), 404
            
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/leaderboard/trend', methods=['GET'])
def get_trend_visualization():
    """
    Endpoint to get visualization of model performance trends
    
    Optional query parameters:
    - models: Comma-separated list of model names
    - metric: The metric to visualize (default: final_score)
    """
    try:
        # Get query parameters
        models_param = request.args.get('models')
        metric = request.args.get('metric', default='final_score')
        
        # Parse models
        models = models_param.split(',') if models_param else None
        
        # Get the visualization
        image_base64 = LeaderboardService.get_trend_visualization(models, metric)
        
        if not image_base64:
            return jsonify({'error': 'Failed to generate visualization'}), 500
            
        return jsonify({
            'image': image_base64,
            'content_type': 'image/png'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/leaderboard/radar', methods=['GET'])
def get_comparison_radar():
    """
    Endpoint to get radar chart comparison of models
    
    Optional query parameters:
    - models: Comma-separated list of model names
    """
    try:
        # Get query parameters
        models_param = request.args.get('models')
        
        # Parse models
        models = models_param.split(',') if models_param else None
        
        # Get the radar chart
        image_base64 = LeaderboardService.get_comparison_radar(models)
        
        if not image_base64:
            return jsonify({'error': 'Failed to generate radar chart'}), 500
            
        return jsonify({
            'image': image_base64,
            'content_type': 'image/png'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 