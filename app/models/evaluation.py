from app import db
from datetime import datetime
import json

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    responses = db.Column(db.JSON, nullable=False)
    scores = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    feedbacks = db.relationship('Feedback', backref='evaluation', lazy=True)
    
    def __init__(self, question, responses, scores):
        self.question = question
        self.responses = responses
        self.scores = scores
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'responses': self.responses,
            'scores': self.scores,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def from_json(json_data):
        return Evaluation(
            question=json_data['question'],
            responses=json_data['responses'],
            scores=json_data['scores']
        ) 