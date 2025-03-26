from app import db
from datetime import datetime

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50), nullable=False)
    avg_coherence = db.Column(db.Float, default=0.0)
    avg_relevance = db.Column(db.Float, default=0.0)
    avg_math_validity = db.Column(db.Float, default=0.0)
    avg_logical_consistency = db.Column(db.Float, default=0.0)
    avg_final_score = db.Column(db.Float, default=0.0)
    total_evaluations = db.Column(db.Integer, default=0)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, model_name, avg_coherence=0.0, avg_relevance=0.0, 
                 avg_math_validity=0.0, avg_logical_consistency=0.0, 
                 avg_final_score=0.0, total_evaluations=0,
                 upvotes=0, downvotes=0):
        self.model_name = model_name
        self.avg_coherence = avg_coherence
        self.avg_relevance = avg_relevance
        self.avg_math_validity = avg_math_validity
        self.avg_logical_consistency = avg_logical_consistency
        self.avg_final_score = avg_final_score
        self.total_evaluations = total_evaluations
        self.upvotes = upvotes
        self.downvotes = downvotes
    
    def to_dict(self):
        return {
            'model': self.model_name,
            'avg_score': self.avg_final_score,
            'total_evaluations': self.total_evaluations,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'metrics': {
                'coherence': self.avg_coherence,
                'relevance': self.avg_relevance,
                'math_validity': self.avg_math_validity,
                'logical_consistency': self.avg_logical_consistency
            }
        }
    
    def update_scores(self, new_scores):
        """
        Update the average scores with new evaluation scores
        """
        old_total = self.total_evaluations
        new_total = old_total + 1
        
        self.avg_coherence = ((self.avg_coherence * old_total) + new_scores['coherence']) / new_total
        self.avg_relevance = ((self.avg_relevance * old_total) + new_scores['relevance']) / new_total
        self.avg_math_validity = ((self.avg_math_validity * old_total) + new_scores['math_validity']) / new_total
        self.avg_logical_consistency = ((self.avg_logical_consistency * old_total) + new_scores['logical_consistency']) / new_total
        self.avg_final_score = ((self.avg_final_score * old_total) + new_scores['final_score']) / new_total
        self.total_evaluations = new_total 