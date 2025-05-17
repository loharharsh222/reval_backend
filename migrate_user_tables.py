from app import create_app, db
import sqlalchemy as sa
from sqlalchemy import inspect

# Create the app and push an application context
app = create_app()
app.app_context().push()

# Connect to database
inspector = inspect(db.engine)

def migrate_user_tables():
    """Create user-related tables if they don't exist"""
    # Check if users table exists
    if not inspector.has_table('users'):
        print("Creating users table...")
        db.create_all()
        print("Users table created successfully.")
    else:
        print("Users table already exists.")

    # Check if user_interactions table exists
    if not inspector.has_table('user_interactions'):
        print("Creating user_interactions table...")
        db.create_all()
        print("User interactions table created successfully.")
    else:
        print("User interactions table already exists.")

# Run migrations
try:
    migrate_user_tables()
    print("Database migration completed!")
except Exception as e:
    print(f"Error during migration: {e}") 