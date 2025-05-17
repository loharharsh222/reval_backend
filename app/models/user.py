from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    clerk_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    interactions = db.relationship('UserInteraction', backref='user', lazy=True)

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Evaluation metrics
    token_overlap = db.Column(db.Float)
    length_ratio = db.Column(db.Float)
    relevance_score = db.Column(db.Float)
    logical_consistency = db.Column(db.Float)
    math_validity = db.Column(db.Float)
    user_rating = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prompt': self.prompt,
            'response': self.response,
            'created_at': self.created_at.isoformat(),
            'metrics': {
                'token_overlap': self.token_overlap,
                'length_ratio': self.length_ratio,
                'relevance_score': self.relevance_score,
                'logical_consistency': self.logical_consistency,
                'math_validity': self.math_validity,
                'user_rating': self.user_rating
            }
        } 