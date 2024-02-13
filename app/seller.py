from app import app, socketio
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from .models import Seller, db
from werkzeug.utils import secure_filename
import os
import uuid

UPLOAD_FOLDER = 'app/static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/dashboard/talent/')
def dashboard():
  return render_template("dashboard.html")


@app.route('/orders')
def orders():
  return render_template('Orders.html')


@app.route('/complete/profile', methods=['GET','POST'])
@login_required
def profile():
  user = current_user
  profile = Seller.query.filter_by(user_id=user.id).first()
  if request.method == 'POST':
        # Retrieve form data
        bio = request.form['bio']
        profile_picture = request.files['profile_picture']
        address = request.form['address']
        skill = request.form['skill']
        city = request.form['city']
        country = request.form['country']
        hourly_rate = request.form['hourly_rate']
        availability = request.form['availability']
        languages = request.form['languages']

         # Handle profile picture upload
        # Grab image name 
        pic_filename = secure_filename(profile_picture.filename)

        # set filename uuid 
        pic_name = str(uuid.uuid4()) + "_" + pic_filename
        # Save image
        profile_picture.save(
            os.path.join(app.config['UPLOAD_FOLDER'],pic_name)
        )

        profile = Seller.query.filter_by(user_id=user.id).first()

        if profile:
            # Update the existing profile
            profile.bio = bio
            profile.address = address
            profile.skill = skill
            profile.city = city
            profile.country = country
            profile.hourly_rate = hourly_rate
            profile.availability = availability
            profile.languages = languages
        else:
            # Create a new Seller instance
            new_seller = Seller(
                bio=bio,
                profile_picture=pic_name,
                address=address,
                skill=skill,
                city=city,
                country=country,
                hourly_rate=hourly_rate,
                availability=availability,
                languages=languages,
                user_id=user.id
            )

            # Add the new seller to the database
            db.session.add(new_seller)

        try:
            # Commit changes to the database
            db.session.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            # Handle database commit error
            db.session.rollback()
            # return render_template('error.html', error_message=str(e))



  user = current_user
  return render_template("profile.html", user=user, profile=profile)

@app.route('/profile/<seller_id>')
@login_required
def view_profile(seller_id):
    if current_user.role == 'seller':
        return redirect(url_for('dashboard'))
    
    seller = Seller.query.filter_by(user_id=seller_id).first()


    return render_template('profile_view.html', seller=seller)

