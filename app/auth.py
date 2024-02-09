from app import (app)
from flask import render_template, redirect, request, flash, url_for
from flask_login import (UserMixin,
                         login_user,
                         LoginManager,
                         login_required,
                         logout_user,
                         current_user)
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from .models import Users, db

bcrypt = Bcrypt(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)

@app.route('/signup', methods=['GET','POST'])
def signup():
  if request.method == 'POST':
    # Let's get user submission from the signup form 
    
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    
    hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Check if the username or email is already registered
    if Users.query.filter_by(email=email).first():
      flash('Looks like this email already has an account with us. Try Logging In','error')
      return redirect(url_for('login'))
    elif Users.query.filter_by(username=username).first():
      flash('This username is unavailable', category='error')
      return redirect(url_for('signup'))
    
    # Validate user creation entries:
     
    # Check password if it matches confirmed password 
    if password != request.form.get('c_password'):
      # Flash error message 
      flash('The Confirm Password does not match the password','error')
    elif not fullname or not email or not username or not password or not role:
      flash('There are missing values in your submission!','error')
    else:
      new_user = Users(
        fullname=fullname,
        email=email,
        password=hashedPassword,
        role=role
      )
      db.session.add(new_user)
      db.session.commit()
  return render_template('signup.html')
  

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('email_or_username')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email_or_username).first() or Users.query.filter_by(username=email_or_username).first()

        if not email_or_username or not password:
            flash('Both email/username and password are required.', category='error')
        if user:
            if bcrypt.check_password_hash(user.password, password):
              
                # Log in the user. remember property set to true 
                login_user(user, 
                           remember=True,
                           duration=3600)
                
                next_page = request.args.get('next')            
                # Redirect to the page specified in query string parameter "next" (if exists), otherwise go back home
                if next_page:
                    flash(f'{current_user.username} You can now access this route!', category='success')
                    return redirect(next_page)
                  
                # Users of different roles get redirected here   
                if user.role == 'customer':
                  flash(f'Welcome back {current_user.fullname}!', category='success')
                  return redirect(url_for('marketplace'))
                flash(f'Welcome back {current_user.fullname}! Ready for new tasks today?', category='success')
                return redirect(url_for('dashboard'))
            flash('Login failed. Please check your email and password.', category='error')    
    return render_template('login.html')



# Logout route   
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))  
  