"""
What do you think the customer will do, or the routes that the customer will access goes here.
Some routes are in the listing file but those also have routes talents will use.

This file will hold the following routes:
/marketplace
/search
/review/<seller_id>



"""
from app import app
from flask import render_template, flash, url_for, redirect, request, jsonify
from flask_login import login_required,current_user
from .models import SellerProfile, User, Rating, db
from sqlalchemy import or_
from functools import cache
from app.analytics import *
from .jobs import create_job
"""

The marketplace is where all the talents will be displayed.
We will use paginate method provided by Flask-sqlalchemy library.
Paginate function will only send requests that the user only asked for.
This prevents all the talents to be displayed once in the marketplace causing  server overlaod.


"""  
@app.route('/marketplace')
@login_required
def marketplace():
    if current_user.role == 'customer':
        page = request.args.get('page', 1, type=int)
        sellers = SellerProfile.query.paginate(per_page=5, page=page, error_out=False)

        # Fetch applications made by the seller to the client's listings
        applications = Application.query.join(Listing, Listing.id == Application.listing_id).\
            filter(Listing.client_id == current_user.id).\
            all()

        return render_template('marketplace.html', sellers=sellers, applications=applications)
    else:
        flash('You are not allowed to view the marketplace', 'error')
        return redirect(url_for('dashboard'))
  

"""

The customer can decide to search for a skill or a specific talent.
This route will facilitate just that.
This route will get the q parameter from url (User request from marketplace search bar)
We will create the logic to allow skill or talent to be returned.


"""    
  
@app.route('/search', methods=['GET'])
@cache
def search_sellers():
    search_query = request.args.get('q')  # Get the search query from the request
    page = request.args.get('page', 1, type=int)

    if not search_query:
        return jsonify({'error': 'No search query provided'}), 400

    # Perform the search based on seller names or skills
    sellers = SellerProfile.query.join(User).filter(
        or_(User.firstname.ilike(f'%{search_query}%'),
            User.lastname.ilike(f'%{search_query}%'),
            SellerProfile.skill.ilike(f'%{search_query}%'))
    ).paginate(per_page=5, page=page, error_out=False)

    if not sellers:
        return jsonify({'message': 'No sellers found matching the search criteria'})

    # Serialize the sellers data to JSON
    sellers_data = [{
        'id': seller.id,
        'full_name': seller.user.get_full_name(),
        'skill': seller.skill,
        'bio': seller.bio,
        'profile_picture': seller.profile_picture,
        'address': seller.address,
        'city': seller.city,
        'country': seller.country,
        'hourly_rate': seller.hourly_rate,
        'availability': seller.availability,
        'is_available': seller.is_available,
        'languages': seller.languages
    } for seller in sellers]

    return render_template(
      'marketplace.html',
      sellers = sellers,
      search_query=search_query
    ) 
    
    
@app.route('/rating/<seller_id>', methods=['POST'])
def create_rating(seller_id):
    data = request.form

    rating = data.get('rating')
    review = data.get('review')
    testimonial = data.get('testimonial')
    customer_id = data.get('customer_id')

    if not rating:
        return jsonify({'error': 'Rating is required'}), 400

    # Check if the seller_id exists
    seller = SellerProfile.query.get(seller_id)
    if not seller:
        return jsonify({'error': 'Seller not found'}), 404

    new_rating = Rating(
        rating=rating,
        review=review,
        testimonial=testimonial,
        customer_id=customer_id,
        seller_id=seller_id
    )

    db.session.add(new_rating)
    db.session.commit()

    return jsonify({'message': 'Rating created successfully'}), 201

@app.route('/client/analytics', methods=['GET'])
@login_required
def client_analytics():
    if current_user.role != 'customer':
        flash('Access denied. Only clients can access this page.', 'danger')
        return redirect(url_for('dashboard')), 403

    client_profile = get_client_profile(current_user.id)
    if not client_profile:
        flash('Client profile not found.', 'danger')
        return redirect(url_for('marketplace'))

    total_jobs, completed_jobs = get_job_stats(client_profile.user_id)
    total_listings, hired_listings = get_listing_stats(client_profile.user_id)
    total_applications, hired_freelancers = get_application_stats(client_profile.user_id)

    return render_template('client/analytics.html',
                           client_profile=client_profile,
                           total_jobs=total_jobs,
                           completed_jobs=completed_jobs,
                           total_listings=total_listings,
                           hired_listings=hired_listings,
                           total_applications=total_applications,
                           hired_freelancers=hired_freelancers)

@app.route('/client/profile', methods=['GET', 'POST'])
def create_client_profile():
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        company_description = request.form.get('company_description')
        company_website = request.form.get('company_website')
        company_address = request.form.get('company_address')
        company_city = request.form.get('company_city')
        company_country = request.form.get('company_country')

        # Get the current user
        user = User.query.get(current_user.id)

        # Create a new ClientProfile instance
        client_profile = ClientProfile(
            user_id=user.id,
            company_name=company_name,
            company_description=company_description,
            company_website=company_website,
            company_address=company_address,
            company_city=company_city,
            company_country=company_country
        )

        # Add the new client profile to the database
        db.session.add(client_profile)
        db.session.commit()

        flash('Client profile created successfully', 'success')
        return redirect(url_for('marketplace'))

    return render_template('client/profile.html')


@app.route('/listings/<listing_id>', methods=['DELETE'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Check if the user has permission to delete the listing
    # (assuming you have some authentication and authorization mechanism in place)
    # if not current_user.can_delete_listing(listing):
    #     return jsonify({'error': 'You are not authorized to delete this listing'}), 403

    try:
        db.session.delete(listing)
        db.session.commit()
        app.logger.info(f"Listing deleted succesfully")
        return jsonify({'message': 'Listing deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting listing: {e}')
        return jsonify({'error': 'An error occurred while deleting the listing'}), 500

@app.route('/listings/<listing_id>/applications', methods=['GET', 'POST'])
@login_required
def view_applications(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # Check if the current user is the client who posted this listing
    # if listing.client_id != current_user.id:
    #     flash('You are not authorized to view applications for this listing.', 'danger')
    #     return redirect(url_for('dashboard'))

    if request.method == 'POST':
        application_id = request.form.get('application_id')
        action = request.form.get('action')

        if action == 'approve':
            application = Application.query.get_or_404(application_id)
            application.approved = True
            db.session.commit()
            create_job()
            flash(f'Application from {application.freelancer.get_full_name()} has been approved.', 'success')
            return redirect(url_for('marketplace'))
        elif action == 'reject':
            application = Application.query.get_or_404(application_id)
            db.session.delete(application)
            db.session.commit()
            flash('Application has been rejected.', 'success')

    applications = Application.query.filter_by(listing_id=listing_id).all()
    return render_template('client/view_applications.html', listing=listing, applications=applications)


