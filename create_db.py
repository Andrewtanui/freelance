from app import create_app
from app.models import db, Users, Seller, Project, Proposal, Review, Message, Notification

# Create the Flask app
app = create_app()

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
