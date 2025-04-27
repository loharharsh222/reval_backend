from app import create_app, db

# Create the app and push an application context
app = create_app()
app.app_context().push()

# Drop all tables
db.drop_all()
print("All tables dropped successfully.")

# Create all tables
db.create_all()
print("All tables created successfully with new schema.")

print("Database reset complete!") 