from app import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, evaluation_id, model_name, vote_type):
        self.evaluation_id = evaluation_id
        self.model_name = model_name
        self.vote_type = vote_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'model_name': self.model_name,
            'vote_type': self.vote_type,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def from_json(json_data):
        return Feedback(
            evaluation_id=json_data['evaluation_id'],
            model_name=json_data['model_name'],
            vote_type=json_data['vote_type']
        ) 