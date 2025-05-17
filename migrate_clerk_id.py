from app import create_app, db
import sqlalchemy as sa
from sqlalchemy import inspect

# Create the app and push an application context
app = create_app()
app.app_context().push()

# Connect to database
inspector = inspect(db.engine)

def migrate_clerk_id():
    """Add clerk_id column to users table if it doesn't exist"""
    if inspector.has_table('users'):
        columns = [column['name'] for column in inspector.get_columns('users')]
        
        if 'clerk_id' not in columns:
            print("Adding clerk_id column to users table...")
            with db.engine.connect() as connection:
                connection.execute(sa.text("ALTER TABLE users ADD COLUMN clerk_id VARCHAR(255) UNIQUE NOT NULL"))
                connection.commit()
            print("clerk_id column added successfully.")
        else:
            print("clerk_id column already exists.")
    else:
        print("Users table doesn't exist. Please run migrate_user_tables.py first.")

# Run migration
try:
    migrate_clerk_id()
    print("Database migration completed!")
except Exception as e:
    print(f"Error during migration: {e}") 