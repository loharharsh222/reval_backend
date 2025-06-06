from app import create_app, db
from sqlalchemy import text

def main():
    # Create app and push context
    app = create_app()
    
    with app.app_context():
        try:
            # Test database connection
            result = db.session.execute(text('SELECT VERSION()'))
            version = result.fetchone()[0]
            print(f"Database version: {version}")
            
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    main()