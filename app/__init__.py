from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database
db = SQLAlchemy()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure database - use SQLite as fallback if PostgreSQL connection fails
    try:
        postgres_uri = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/llm_eval')
        app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Test PostgreSQL connection
        from sqlalchemy import create_engine
        engine = create_engine(postgres_uri)
        connection = engine.connect()
        connection.close()
        print("Connected to PostgreSQL database successfully!")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Using SQLite database as fallback")
        # Use SQLite as fallback
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///llm_eval.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize CORS
    CORS(app)
    
    # Initialize database with app
    db.init_app(app)
    
    # Import and register blueprints
    from app.controllers.evaluation_controller import evaluation_bp
    from app.controllers.feedback_controller import feedback_bp
    from app.controllers.leaderboard_controller import leaderboard_bp
    
    app.register_blueprint(evaluation_bp, url_prefix='/api')
    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(leaderboard_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 