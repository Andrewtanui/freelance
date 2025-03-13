from app import app
from app.models import db

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
