from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
import datetime
from flask_migrate import Migrate

# Set up the application context
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(UserMixin, db.Model):
    """Users model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.String(15), unique=False, nullable=True)

    # Update this relationship
    viewed_sellers = db.relationship('ViewedCustomers', back_populates='customer')

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

    # Update this relationship
    viewed_customers = db.relationship('ViewedCustomers', back_populates='seller')


class ViewedCustomers(db.Model):
    __tablename__ = 'viewed_customers'
    seller_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    seller = db.relationship('Seller', back_populates='viewed_customers')
    customer = db.relationship('Users', back_populates='viewed_sellers')
