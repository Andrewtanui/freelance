from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate
from datetime import datetime
import uuid
from app import app
# Create Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize SQLAlchemy instance with the app
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set up the application context
app.app_context().push()

def generate_unique_uuid():
    while True:
        new_uuid = str(uuid.uuid4())
        # Check if the generated UUID already exists in the database
        existing_user = User.query.filter_by(id=new_uuid).first()
        if not existing_user:
            return new_uuid

class User(UserMixin, db.Model):
    """Users model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.String(15), unique=False, nullable=True)

    profile = db.relationship("SellerProfile", backref="user", uselist=False)
    client_profile = db.relationship("ClientProfile", backref="user", uselist=False)
    sent_messages = db.relationship("Message", backref="sender_user", lazy="select", foreign_keys="Message.sender_id")
    received_messages = db.relationship("Message", backref="recipient_user", lazy="select", foreign_keys="Message.recipient_id")
    listings = db.relationship("Listing", backref="client", lazy="select")
    applications = db.relationship("Application", backref="freelancer", lazy="select")
    notifications_s = db.relationship("Notification", backref='notifications', lazy="select")
    ratings_given = db.relationship("Rating", backref="rating_customer", lazy="select", foreign_keys="Rating.customer_id")

    def get_full_name(self):
        """Method to fetch the full name"""
        return f"{self.firstname} {self.lastname}"

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    body = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)

    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    recipient_id = db.Column(db.String(36), db.ForeignKey('users.id'))

class SellerProfile(db.Model):
    """Profile model for storing user profiles"""
    __tablename__ = 'seller_profiles'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
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
    portfolio_items_seller = db.relationship('PortfolioItem', backref='seller_profile', lazy=True)
    ratings = db.relationship('Rating', backref='rated_seller', lazy=True)

class ClientProfile(db.Model):
    """Client profile model for storing client-specific information"""
    __tablename__ = 'client_profiles'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(64), nullable=False)
    company_description = db.Column(db.Text, nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    company_address = db.Column(db.String(255), nullable=False)
    company_city = db.Column(db.String(64), nullable=False)
    company_country = db.Column(db.String(64), nullable=False)

    profile_client = db.relationship('User', backref='user_client_profile', uselist=False, lazy=True,
                                     primaryjoin="ClientProfile.user_id == User.id")

    def __repr__(self):
        return f"<ClientProfile(id='{self.id}', company_name='{self.company_name}')>"

class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(255), nullable=True)

    seller_id = db.Column(db.String(36), db.ForeignKey('seller_profiles.id'), nullable=False)
    seller = db.relationship('SellerProfile', backref='portfolio_items', lazy=True)

    def __repr__(self):
        return f"<PortfolioItem(id='{self.id}', title='{self.title}', file_path='{self.file_path}', url='{self.url}')>"

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    testimonial = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('seller_profiles.id'), nullable=False)

    customer = db.relationship('User', foreign_keys=[customer_id])
    seller = db.relationship('SellerProfile', foreign_keys=[seller_id])

    def __repr__(self):
        return f"<Rating(id='{self.id}', rating={self.rating}, review='{self.review[:20]}...', testimonial='{self.testimonial[:20]}...')>"

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    budget = db.Column(db.Numeric(10, 2))
    deadline = db.Column(db.DateTime)

    client_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    applications = db.relationship("Application", backref="listing", lazy="select")

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    cover_letter = db.Column(db.Text)

    freelancer_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    listing_id = db.Column(db.String(36), db.ForeignKey('listings.id'))

class NotificationType(db.Model):
    __tablename__ = 'notification_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<NotificationType(name='{self.name}')>"

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('notification_types.id'), nullable=False)

    user_notification = db.relationship('User', backref='notifications', lazy='select', overlaps="notifications_s,notifications")
    type = db.relationship('NotificationType', backref='notifications')

    def __repr__(self):
        return f"<Notification(id='{self.id}', message='{self.message[:20]}...', is_read={self.is_read})>"

class ActivityType(db.Model):
    __tablename__ = 'activity_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<ActivityType(name='{self.name}')>"

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('activity_types.id'), nullable=False)

    user = db.relationship('User', backref='activities')
    type = db.relationship('ActivityType', backref='activities')

    def __repr__(self):
        return f"<Activity(id='{self.id}', description='{self.description[:20]}...')>"

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    client_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    freelancer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=False)

    client = db.relationship('User', backref='jobs_as_client', foreign_keys=[client_id])
    freelancer = db.relationship('User', backref='jobs_as_freelancer', foreign_keys=[freelancer_id])
    listing = db.relationship('Listing', backref='job')
    deliverables = db.relationship('Deliverable', backref='job', lazy=True)
    payments = db.relationship('Payment', backref='job', lazy=True)

    def __repr__(self):
        return f"<Job(id='{self.id}', title='{self.title}', status='{self.status}')>"

class Deliverable(db.Model):
    __tablename__ = 'deliverables'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)

    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)

    def __repr__(self):
        return f"<Deliverable(id='{self.id}', title='{self.title}', approved={self.approved})>"

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)

    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)

    def __repr__(self):
        return f"<Payment(id='{self.id}', amount={self.amount}, currency='{self.currency}', payment_method='{self.payment_method}')>"