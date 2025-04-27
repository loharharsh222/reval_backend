from app import db
from datetime import datetime

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50), nullable=False)
    avg_coherence = db.Column(db.Float, default=0.0)
    avg_token_overlap = db.Column(db.Float, default=0.0)
    avg_length_ratio = db.Column(db.Float, default=0.0)
    avg_final_score = db.Column(db.Float, default=0.0)
    total_evaluations = db.Column(db.Integer, default=0)
    user_rating = db.Column(db.Float, default=0.0)
    feedback_count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, model_name, avg_coherence=0.0, avg_token_overlap=0.0, 
                 avg_length_ratio=0.0, avg_final_score=0.0, total_evaluations=0,
                 user_rating=0.0, feedback_count=0):
        self.model_name = model_name
        self.avg_coherence = avg_coherence
        self.avg_token_overlap = avg_token_overlap
        self.avg_length_ratio = avg_length_ratio
        self.avg_final_score = avg_final_score
        self.total_evaluations = total_evaluations
        self.user_rating = user_rating
        self.feedback_count = feedback_count
    
    def to_dict(self):
        return {
            'model': self.model_name,
            'avg_score': self.avg_final_score,
            'total_evaluations': self.total_evaluations,
            'user_rating': self.user_rating,
            'feedback_count': self.feedback_count,
            'metrics': {
                'coherence': self.avg_coherence,
                'token_overlap': self.avg_token_overlap,
                'length_ratio': self.avg_length_ratio
            }
        }
    
    def update_scores(self, new_scores):
        """
        Update the average scores with new evaluation scores
        """
        old_total = self.total_evaluations
        new_total = old_total + 1
        
        self.avg_coherence = ((self.avg_coherence * old_total) + new_scores['coherence']) / new_total
        self.avg_token_overlap = ((self.avg_token_overlap * old_total) + new_scores['token_overlap']) / new_total
        self.avg_length_ratio = ((self.avg_length_ratio * old_total) + new_scores['length_ratio']) / new_total
        self.avg_final_score = ((self.avg_final_score * old_total) + new_scores['overall_score']) / new_total
        self.total_evaluations = new_total
    
    def update_user_rating(self, rating):
        """
        Update the average user rating
        
        Args:
            rating: New user rating (1-5)
        """
        old_total = self.feedback_count
        new_total = old_total + 1
        
        self.user_rating = ((self.user_rating * old_total) + rating) / new_total
        self.feedback_count = new_total 