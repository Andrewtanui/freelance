from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import Users, db, Seller
from . import login_manager
from datetime import datetime, timedelta

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        role = request.form.get('role')
        phonenumber = request.form.get('phonenumber')

        # Check if user already exists
        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # Create new user
        new_user = Users(
            email=email,
            username=username,
            password=generate_password_hash(password, method='scrypt'),
            firstname=firstname,
            lastname=lastname,
            role=role,
            phonenumber=phonenumber,
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # If user is a seller, create seller profile
            if role == 'seller':
                skills = request.form.get('skills', '')
                hourly_rate = request.form.get('hourly_rate', 0)
                bio = request.form.get('bio', '')

                seller_profile = Seller(
                    user_id=new_user.id,
                    skills=skills,
                    hourly_rate=float(hourly_rate) if hourly_rate else 0,
                    bio=bio,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(seller_profile)
                db.session.commit()

            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('auth.signup'))

    return render_template('signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = Users.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        duration = timedelta(days=2)
        login_user(user, remember=remember, duration=duration)
        
        next_page = request.args.get('next')            
        # Redirect to the page specified in query string parameter "next" (if exists), otherwise go back home
        if next_page:
            flash(f'{current_user.firstname} You can now access this route!', category='success')
            return redirect(next_page)
          
        # Users of different roles get redirected here
        if user.role == 'customer':
            flash(f'Welcome back {current_user.firstname}!', category='success')
            return redirect(url_for('views.marketplace'))
        flash(f'Welcome back {current_user.firstname}! Ready for new tasks today?', category='success')
        return redirect(url_for('views.dashboard'))

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
