from math import ceil
from app import app
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from .models import SellerProfile, db
from werkzeug.utils import secure_filename
import os
import uuid
from app.notifications import send_notification
from app.analytics import *

UPLOAD_FOLDER = 'app/static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/dashboard/talent/')
@login_required
def dashboard():
    seller_profile = get_seller_profile(current_user.id)
  
    total_ratings, average_rating = get_rating_stats(seller_profile.id) or None
    total_deliverables, approved_deliverables = get_deliverable_stats(seller_profile.id)
    total_jobs, completed_jobs = get_job_stats(seller_profile.id)

    return render_template("dashboard.html",
                           seller_profile=seller_profile,
                           total_ratings=total_ratings,
                           average_rating=average_rating,
                           total_deliverables=total_deliverables,
                           approved_deliverables=approved_deliverables,
                           total_jobs=total_jobs,
                           completed_jobs=completed_jobs)


@app.route('/orders')
def orders():
  return render_template('Orders.html')


@app.route('/seller/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user=current_user
    if current_user.role != 'seller':
        flash('Access denied. Only sellers can access this page.', 'danger')
        return redirect(url_for('main.index'))

    profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        try:
            bio = request.form.get('bio')
            address = request.form.get('address')
            skill = request.form.get('skill')
            city = request.form.get('city')
            country = request.form.get('country')
            hourly_rate = request.form.get('hourly_rate')
            availability = request.form.get('availability')
            is_available = request.form.get('is_available', False)
            languages = request.form.get('languages')

            new_profile = SellerProfile(
                user_id=current_user.id,
                bio=bio,
                address=address,
                skill=skill,
                city=city,
                country=country,
                hourly_rate=hourly_rate,
                availability=availability,
                is_available=bool(is_available),
                languages=languages
            )
            db.session.add(new_profile)
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('profile.html', profile=profile, user=user)

@app.route('/profile/<seller_id>')
@login_required
def view_profile(seller_id):
    if current_user.role == 'seller':
        return redirect(url_for('dashboard'))
    seller = SellerProfile.query.filter_by(user_id=seller_id).first()

    # When a client views a seller's profile
    send_notification(seller.user.id, 'profile_view', {'viewer': current_user.get_full_name()})

    return render_template('profile_view.html', seller=seller)


# When a client views a seller's profile
# send_notification(seller.user.id, 'profile_view', {'viewer': current_user.get_full_name()})

# When a new message is sent
# send_notification(recipient.id, 'new_message', {'sender': sender.get_full_name(), 'body': message.body})

#Update user profile
@app.route('/update/profile/<id>', methods=['POST'])
@login_required
def updateSellerProfile(id):
    update_profile = SellerProfile.query.get_or_404(id)
    if not update_profile:
        flash("You haven't completed your profile.","warning")
        return redirect(url_for('profile'))
    else:
        try:
            bio = request.form.get('bio')
            address = request.form.get('address')
            skill = request.form.get('skill')
            city = request.form.get('city')
            country = request.form.get('country')
            hourly_rate = request.form.get('hourly_rate')
            availability = request.form.get('availability')
            is_available = request.form.get('is_available', False)
            languages = request.form.get('languages')

            profile.bio = bio or profile.bio
            profile.address = address or profile.address
            profile.skill = skill or profile.skill
            profile.city = city or profile.city
            profile.country = country or profile.country
            profile.hourly_rate = hourly_rate or profile.hourly_rate
            profile.availability = availability or profile.availability
            profile.is_available = bool(is_available) or profile.is_available
            profile.languages = languages or profile.languages

            db.session.commit()
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/seller/analytics', methods=['GET'])
@login_required
def seller_analytics():
    if current_user.role != 'seller':
        flash('Access denied. Only sellers can access this page.', 'danger')
        return redirect(url_for('marketplace'))

    seller_profile = get_seller_profile(current_user.id)
    if not seller_profile:
        flash('Seller profile not found.', 'danger')
        return redirect(url_for('profile'))

    total_ratings, average_rating = get_rating_stats(seller_profile.id)
    total_deliverables, approved_deliverables = get_deliverable_stats(seller_profile.id)
    total_jobs, completed_jobs = get_job_stats(seller_profile.id)

    return render_template('sellers/analytics.html',
                           seller_profile=seller_profile,
                           total_ratings=total_ratings,
                           average_rating=average_rating,
                           total_deliverables=total_deliverables,
                           approved_deliverables=approved_deliverables,
                           total_jobs=total_jobs,
                           completed_jobs=completed_jobs)


@app.route('/listings', methods=['GET'])
def get_matching_listings():
    # Get the seller profile from the authenticated user
    if not current_user.is_authenticated or current_user.role != 'seller':
        return jsonify({'error': 'Unauthorized access'}), 401

    seller_profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    if not seller_profile:
        return jsonify({'error': 'Seller profile not found'}), 404

    # Get the seller's skill
    seller_skill = seller_profile.skill

    # Get the current page number
    page = request.args.get('page', 1, type=int)

    # Set the number of listings per page
    per_page = 9

    # Query the Listing model to find listings that match the seller's skill
    matching_listings = Listing.query.join(User, Listing.client_id == User.id) \
                                .join(ClientProfile, User.id == ClientProfile.user_id) \
                                .filter(ClientProfile.company_description.ilike(f'%{seller_skill}%')) \
                                .paginate(page=page, per_page=per_page)

    listings_data = [
        {
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'budget': float(listing.budget) if listing.budget is not None else 0.0,
            'deadline': listing.deadline.isoformat() if listing.deadline else None,
            'client_name': listing.client.get_full_name()
        }
        for listing in matching_listings.items
    ]

    total_pages = ceil(matching_listings.total / per_page)

    return render_template('sellers/listings.html', listings=listings_data, current_page=page, total_pages=total_pages)


@app.route('/listings/<listing_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_for_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    seller_profile = SellerProfile.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '')

        # Check if the seller has already applied for this listing
        existing_application = Application.query.filter_by(freelancer_id=current_user.id, listing_id=listing_id).first()
        if existing_application:
            flash('You have already applied for this listing.', 'warning')
            return redirect(url_for('get_matching_listings'))

        new_application = Application(
            cover_letter=cover_letter,
            freelancer_id=current_user.id,
            listing_id=listing_id
        )

        db.session.add(new_application)
        db.session.commit()

        flash('Your application has been submitted successfully.', 'success')
        return redirect(url_for('get_matching_listings'))

    return render_template('sellers/apply_for_listing.html', listing=listing, seller_profile=seller_profile)






