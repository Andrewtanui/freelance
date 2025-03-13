from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
from datetime import datetime

# Set up the application context
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Users(UserMixin, db.Model):
    """Users model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.String(15), unique=False, nullable=True)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True, foreign_keys='Project.client_id')
    proposals = db.relationship('Proposal', backref='freelancer', lazy=True, foreign_keys='Proposal.freelancer_id')
    reviews_given = db.relationship('Review', backref='reviewer', lazy=True, foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', backref='reviewee', lazy=True, foreign_keys='Review.reviewee_id')
    messages_sent = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='receiver', lazy=True, foreign_keys='Message.receiver_id')

    def __init__(self, firstname, lastname, password, email, role, phonenumber):
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.email = email
        self.role = role
        self.phonenumber = phonenumber

    def get_full_name(self):
        """Method to fetch the full name"""
        return f"{self.firstname} {self.lastname}"


class Seller(db.Model):
    """Profile model for storing user profiles"""
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(64), unique=False, nullable=False)
    skill = db.Column(db.String(64), unique=False, nullable=False)
    city = db.Column(db.String(64), unique=False, nullable=False)
    country = db.Column(db.String(64), unique=False, nullable=False)
    
    hourly_rate = db.Column(db.Float, nullable=True)
    availability = db.Column(db.String(50), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    languages = db.Column(db.String(255), nullable=True)
    
    user = db.relationship('Users', backref='profile', uselist=False, lazy=True)

    def __init__(self, user_id, address, skill, city, country, bio=None, profile_picture=None,
                 hourly_rate=None, availability=None, is_available=True, languages=None):
        self.user_id = user_id
        self.bio = bio
        self.profile_picture = profile_picture
        self.address = address
        self.skill = skill
        self.city = city
        self.country = country
        self.hourly_rate = hourly_rate
        self.availability = availability
        self.is_available = is_available
        self.languages = languages


class Project(db.Model):
    """Project model for storing project details"""
    __tablename__ = 'projects'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    skills_required = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='open', nullable=False)  # open, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    client_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    awarded_to = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    proposals = db.relationship('Proposal', backref='project', lazy=True)
    
    def __init__(self, title, description, budget, category, client_id, deadline=None, skills_required=None):
        self.title = title
        self.description = description
        self.budget = budget
        self.category = category
        self.client_id = client_id
        self.deadline = deadline
        self.skills_required = skills_required


class Proposal(db.Model):
    """Proposal model for storing freelancer proposals for projects"""
    __tablename__ = 'proposals'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    estimated_completion_time = db.Column(db.Integer, nullable=True)  # in days
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    freelancer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, bid_amount, cover_letter, project_id, freelancer_id, estimated_completion_time=None):
        self.bid_amount = bid_amount
        self.cover_letter = cover_letter
        self.project_id = project_id
        self.freelancer_id = freelancer_id
        self.estimated_completion_time = estimated_completion_time


class Review(db.Model):
    """Review model for storing reviews between users"""
    __tablename__ = 'reviews'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    reviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reviewee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, rating, project_id, reviewer_id, reviewee_id, comment=None):
        self.rating = rating
        self.project_id = project_id
        self.reviewer_id = reviewer_id
        self.reviewee_id = reviewee_id
        self.comment = comment


class Message(db.Model):
    """Message model for storing messages between users"""
    __tablename__ = 'messages'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=True)
    
    def __init__(self, content, sender_id, receiver_id, project_id=None):
        self.content = content
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.project_id = project_id
