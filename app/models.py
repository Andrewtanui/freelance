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


def generate_unique_uuid():
    while True:
        new_uuid = str(uuid.uuid4())
        # Check if the generated UUID already exists in the database
        existing_user = Users.query.filter_by(id=new_uuid).first()
        if not existing_user:
            return new_uuid

class Users(UserMixin, db.Model):
    """Users model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_unique_uuid, unique=True, nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.String(15), unique=False, nullable=True)


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
    ratings = db.relationship('Ratings', backref='seller', lazy=True)


class Ratings(db.Model):
    """Ratings model for storing user ratings"""
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    
    customer = db.relationship('Users', foreign_keys=[customer_id])
    seller = db.relationship('Seller', foreign_keys=[seller_id])
    
class Listing(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200)) 
  description = db.Column(db.Text)
  budget = db.Column(db.Numeric(10,2))
  deadline = db.Column(db.DateTime)
  
  client_id = db.Column(db.String(36), db.ForeignKey('users.id'))
  client = db.relationship('User', backref='listings')
  
class Application(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cover_letter = db.Column(db.Text)
  
  freelancer_id = db.Column(db.String(36), db.ForeignKey('users.id'))
  freelancer = db.relationship('User', backref='applications')

  listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
  listing = db.relationship('Listing', backref='applications')
  

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.Text)
  sent_at = db.Column(db.DateTime)

  sender_id = db.Column(db.String(36), db.ForeignKey('users.id'))
  sender = db.relationship('User', foreign_keys=[sender_id])

  recipient_id = db.Column(db.String(36), db.ForeignKey('users.id'))
  recipient = db.relationship('User', foreign_keys=[recipient_id])        
  
  
  
class Notification(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.Text)
  is_read = db.Column(db.Boolean, default=False)

  user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
  user = db.relationship('User', backref='notifications')  
  