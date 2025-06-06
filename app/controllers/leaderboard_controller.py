from flask import Blueprint, request, jsonify
from app.services.leaderboard_service import LeaderboardService
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.evaluation import Evaluation

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

@leaderboard_bp.route('/api/trends', methods=['GET'])
def get_trends():
    """
    Endpoint to get historical performance trends for models
    
    Optional query parameters:
    - days: Number of days to look back (default: 30)
    - models: Comma-separated list of model names to include
    """
    try:
        # Get query parameters
        days = request.args.get('days', default=30, type=int)
        models_param = request.args.get('models')
        
        # Parse models if specified
        specific_models = models_param.split(',') if models_param else None
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        # Get historical data from database
        from app import db
        
        # Query evaluations grouped by date and model
        query = db.session.query(
            func.date(Evaluation.created_at).label('date'),
            Evaluation.model_name,
            func.avg(Evaluation.final_score).label('avg_score'),
            func.count(Evaluation.id).label('evaluation_count')
        ).filter(
            Evaluation.created_at >= start_date,
            Evaluation.created_at <= end_date
        ).group_by(
            func.date(Evaluation.created_at),
            Evaluation.model_name
        ).order_by(func.date(Evaluation.created_at))
        
        # Filter by specific models if requested
        if specific_models:
            query = query.filter(Evaluation.model_name.in_(specific_models))
        
        results = query.all()
        
        # Organize data by date
        data_by_date = {}
        all_models = set()
        
        for result in results:
            date_str = result.date.strftime("%b %d")
            model_name = result.model_name
            avg_score = float(result.avg_score) if result.avg_score else 0.0
            
            if date_str not in data_by_date:
                data_by_date[date_str] = {
                    'date': date_str,
                    'timestamp': int(result.date.timestamp() * 1000)
                }
            
            data_by_date[date_str][model_name] = round(avg_score, 3)
            all_models.add(model_name)
        
        # Fill in missing dates and models with None values
        historical_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%b %d")
            
            if date_str in data_by_date:
                day_data = data_by_date[date_str]
            else:
                day_data = {
                    'date': date_str,
                    'timestamp': int(current_date.timestamp() * 1000)
                }
            
            # Ensure all models have entries (None if no data)
            for model in all_models:
                if model not in day_data:
                    day_data[model] = None
            
            historical_data.append(day_data)
            current_date += timedelta(days=1)
        
        # If no data found, return sample data for demonstration
        if not historical_data or not any(any(k not in ['date', 'timestamp'] for k in day.keys()) for day in historical_data):
            import random
            import math
            
            historical_data = []
            sample_models = ['ChatGPT', 'Gemini', 'Llama', 'Claude']
            
            for i in range(days):
                date = end_date - timedelta(days=days-1-i)
                
                day_data = {
                    "date": date.strftime("%b %d"),
                    "timestamp": int(date.timestamp() * 1000)
                }
                
                # Generate realistic sample data
                base_day = i
                for j, model in enumerate(sample_models):
                    base_score = 0.65 + (j * 0.05)  # Different base scores
                    trend = math.sin(base_day * 0.1 + j) * 0.1
                    growth = base_day * 0.002
                    noise = random.uniform(-0.03, 0.03)
                    
                    score = base_score + trend + growth + noise
                    day_data[model] = round(min(1.0, max(0.0, score)), 3)
                
                historical_data.append(day_data)
        
        return jsonify({
            'data': historical_data,
            'models': list(all_models) if all_models else ['ChatGPT', 'Gemini', 'Llama', 'Claude'],
            'date_range': {
                'start': start_date.strftime("%Y-%m-%d"),
                'end': end_date.strftime("%Y-%m-%d"),
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/ranking', methods=['GET'])
def get_ranking():
    """
    Endpoint to get current model rankings
    
    Optional query parameters:
    - metric: Metric to rank by (default: final_score)
    - limit: Number of models to return (default: 10)
    """
    try:
        metric = request.args.get('metric', default='final_score')
        limit = request.args.get('limit', default=10, type=int)
        
        # Get ranking data using existing leaderboard service
        leaderboard_data = LeaderboardService.get_leaderboard(limit)
        
        # Transform to ranking format
        ranking = []
        for i, entry in enumerate(leaderboard_data.get('leaderboard', []), 1):
            ranking.append({
                'rank': i,
                'model': entry.get('model_name'),
                'score': entry.get('final_score', 0),
                'evaluations': entry.get('total_evaluations', 0),
                'change': 0  # You can implement rank change tracking
            })
        
        return jsonify({
            'ranking': ranking,
            'metric': metric,
            'total_models': len(ranking)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500