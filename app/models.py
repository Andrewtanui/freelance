from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid as uuid



# Set up the application context
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    """Users model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    fullname = db.Column(db.String(64), unique=False, nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(10), nullable=False)

    def __init__(self, username, fullname, password, email, role):
        self.username = username
        self.fullname = fullname
        self.password = password
        self.email = email
        self.role = role
        


class Seller(db.Model):
    """Profile model for storing user profiles"""
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255),nullable=True)
    phonenumber = db.Column(db.Integer, unique=False, nullable=False)
    address = db.Column(db.String(64), unique=False, nullable=False)
    skill = db.Column(db.String(64), unique=False, nullable=False)
    city = db.Column(db.String(64), unique=False, nullable=False)
    country = db.Column(db.String(64), unique=False, nullable=False)
    
    user = db.relationship('Users', backref='profile', uselist=False, lazy=True)

    def __init__(self, user_id, bio=None, profile_picture=None):
        self.user_id = user_id
        self.bio = bio
        self.profile_picture = profile_picture        
        