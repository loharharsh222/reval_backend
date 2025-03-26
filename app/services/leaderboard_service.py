from app.models.leaderboard import Leaderboard
from app.models.evaluation import Evaluation
from app.utils.visualization import Visualization
from app import db
from sqlalchemy import desc
import json

class LeaderboardService:
    @staticmethod
    def get_leaderboard(limit=10):
        """
        Get the current leaderboard rankings
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of leaderboard entries sorted by average final score
        """
        leaderboard_entries = Leaderboard.query.order_by(desc(Leaderboard.avg_final_score)).limit(limit).all()
        return [entry.to_dict() for entry in leaderboard_entries]
    
    @staticmethod
    def get_model_metrics(model_name):
        """
        Get detailed metrics for a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary of model metrics and stats
        """
        # Get the leaderboard entry
        leaderboard_entry = Leaderboard.query.filter_by(model_name=model_name).first()
        if not leaderboard_entry:
            return None
        
        # Get recent evaluations for this model
        recent_evaluations = Evaluation.query.order_by(desc(Evaluation.created_at)).limit(100).all()
        recent_scores = []
        
        for eval_record in recent_evaluations:
            if model_name in eval_record.scores:
                recent_scores.append({
                    'question': eval_record.question,
                    'scores': eval_record.scores[model_name],
                    'created_at': eval_record.created_at.isoformat()
                })
        
        # Return the model metrics and stats
        return {
            'model': model_name,
            'metrics': {
                'coherence': leaderboard_entry.avg_coherence,
                'relevance': leaderboard_entry.avg_relevance,
                'math_validity': leaderboard_entry.avg_math_validity,
                'logical_consistency': leaderboard_entry.avg_logical_consistency,
                'final_score': leaderboard_entry.avg_final_score
            },
            'stats': {
                'total_evaluations': leaderboard_entry.total_evaluations,
                'upvotes': leaderboard_entry.upvotes,
                'downvotes': leaderboard_entry.downvotes
            },
            'recent_scores': recent_scores[:10]  # Limit to 10 most recent
        }
    
    @staticmethod
    def get_trend_visualization(models=None, metric='final_score'):
        """
        Generate a visualization of model performance trends
        
        Args:
            models: List of model names to include (None for all)
            metric: The metric to visualize
            
        Returns:
            Base64 encoded PNG image
        """
        # If no models specified, use top 5
        if not models:
            top_models = Leaderboard.query.order_by(desc(Leaderboard.avg_final_score)).limit(5).all()
            models = [model.model_name for model in top_models]
        
        # Get all evaluations
        evaluations = Evaluation.query.order_by(Evaluation.created_at).all()
        
        # Generate and return the visualization
        image_base64 = Visualization.generate_leaderboard_trend(models, evaluations, metric)
        return image_base64
    
    @staticmethod
    def get_comparison_radar(models=None):
        """
        Generate a radar chart comparing different models across metrics
        
        Args:
            models: List of model names to include (None for all)
            
        Returns:
            Base64 encoded PNG image
        """
        # If no models specified, use top 5
        if not models:
            top_models = Leaderboard.query.order_by(desc(Leaderboard.avg_final_score)).limit(5).all()
            model_names = [model.model_name for model in top_models]
        else:
            model_names = models
            
        # Get the model scores
        model_scores = {}
        for name in model_names:
            model = Leaderboard.query.filter_by(model_name=name).first()
            if model:
                model_scores[name] = {
                    'coherence': model.avg_coherence,
                    'relevance': model.avg_relevance,
                    'math_validity': model.avg_math_validity,
                    'logical_consistency': model.avg_logical_consistency,
                    'final_score': model.avg_final_score
                }
        
        # Generate and return the radar chart
        image_base64 = Visualization.generate_radar_chart(model_scores)
        return image_base64 