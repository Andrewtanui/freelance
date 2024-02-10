from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

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
