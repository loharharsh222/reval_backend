from app.models.feedback import Feedback
from app.models.leaderboard import Leaderboard
from app import db

class FeedbackService:
    @staticmethod
    def save_feedback(evaluation_id, model_name, vote_type):
        """
        Save user feedback (upvote/downvote) for a model's response
        
        Args:
            evaluation_id: ID of the evaluation
            model_name: Name of the model to receive feedback
            vote_type: 'upvote' or 'downvote'
            
        Returns:
            Created feedback object
        """
        # Validate vote type
        if vote_type not in ['upvote', 'downvote']:
            raise ValueError("Vote type must be 'upvote' or 'downvote'")
        
        # Create and save the feedback
        feedback = Feedback(
            evaluation_id=evaluation_id,
            model_name=model_name,
            vote_type=vote_type
        )
        
        db.session.add(feedback)
        
        # Update leaderboard stats
        leaderboard_entry = Leaderboard.query.filter_by(model_name=model_name).first()
        if leaderboard_entry:
            if vote_type == 'upvote':
                leaderboard_entry.upvotes += 1
            else:
                leaderboard_entry.downvotes += 1
        
        db.session.commit()
        
        return feedback
    
    @staticmethod
    def get_feedback_stats(evaluation_id=None, model_name=None):
        """
        Get feedback statistics
        
        Args:
            evaluation_id: Optional - filter by evaluation ID
            model_name: Optional - filter by model name
            
        Returns:
            Dictionary of feedback statistics
        """
        # Build query based on filters
        query = Feedback.query
        
        if evaluation_id:
            query = query.filter_by(evaluation_id=evaluation_id)
        
        if model_name:
            query = query.filter_by(model_name=model_name)
        
        # Get all matching feedback entries
        feedbacks = query.all()
        
        # Calculate stats
        upvotes = sum(1 for f in feedbacks if f.vote_type == 'upvote')
        downvotes = sum(1 for f in feedbacks if f.vote_type == 'downvote')
        total = len(feedbacks)
        
        # Organize by model if not filtered by model
        model_stats = {}
        if not model_name:
            for feedback in feedbacks:
                if feedback.model_name not in model_stats:
                    model_stats[feedback.model_name] = {'upvotes': 0, 'downvotes': 0}
                
                if feedback.vote_type == 'upvote':
                    model_stats[feedback.model_name]['upvotes'] += 1
                else:
                    model_stats[feedback.model_name]['downvotes'] += 1
        
        return {
            'total_feedbacks': total,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'model_stats': model_stats
        } 