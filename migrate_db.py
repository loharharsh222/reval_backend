from app import create_app, db
import sqlalchemy as sa
from sqlalchemy import inspect, Column, Float, Integer, DateTime, String
from datetime import datetime

# Create the app and push an application context
app = create_app()
app.app_context().push()

# Connect to database
inspector = inspect(db.engine)

def migrate_leaderboard_table():
    """Migrate the leaderboard table to include new columns"""
    # Check if table exists
    if not inspector.has_table('leaderboard'):
        print("Leaderboard table doesn't exist. No migration needed.")
        return
    
    # Get existing columns
    columns = [column['name'] for column in inspector.get_columns('leaderboard')]
    
    # Add new columns if they don't exist
    with db.engine.connect() as connection:
        if 'avg_token_overlap' not in columns:
            print("Adding avg_token_overlap column...")
            connection.execute(sa.text("ALTER TABLE leaderboard ADD COLUMN avg_token_overlap FLOAT DEFAULT 0.0"))
        
        if 'avg_length_ratio' not in columns:
            print("Adding avg_length_ratio column...")
            connection.execute(sa.text("ALTER TABLE leaderboard ADD COLUMN avg_length_ratio FLOAT DEFAULT 0.0"))
        
        if 'user_rating' not in columns:
            print("Adding user_rating column...")
            connection.execute(sa.text("ALTER TABLE leaderboard ADD COLUMN user_rating FLOAT DEFAULT 0.0"))
        
        if 'feedback_count' not in columns:
            print("Adding feedback_count column...")
            connection.execute(sa.text("ALTER TABLE leaderboard ADD COLUMN feedback_count INTEGER DEFAULT 0"))
        
        # Remove old columns if they exist
        if 'avg_relevance' in columns:
            print("Removing avg_relevance column...")
            connection.execute(sa.text("ALTER TABLE leaderboard DROP COLUMN avg_relevance"))
        
        if 'avg_math_validity' in columns:
            print("Removing avg_math_validity column...")
            connection.execute(sa.text("ALTER TABLE leaderboard DROP COLUMN avg_math_validity"))
        
        if 'avg_logical_consistency' in columns:
            print("Removing avg_logical_consistency column...")
            connection.execute(sa.text("ALTER TABLE leaderboard DROP COLUMN avg_logical_consistency"))
        
        if 'upvotes' in columns:
            print("Removing upvotes column...")
            connection.execute(sa.text("ALTER TABLE leaderboard DROP COLUMN upvotes"))
        
        if 'downvotes' in columns:
            print("Removing downvotes column...")
            connection.execute(sa.text("ALTER TABLE leaderboard DROP COLUMN downvotes"))
        
        # Commit the transaction
        connection.commit()
    
    print("Leaderboard table migration completed successfully.")

# Run migrations
try:
    migrate_leaderboard_table()
    print("Database migration completed!")
except Exception as e:
    print(f"Error during migration: {e}") 