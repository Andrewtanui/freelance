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
from .models import Seller, Users, Ratings, db
from sqlalchemy import or_

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
    
    sellers = Seller.query.paginate(per_page=5, page=page, error_out=False)
    
    return render_template('viewProfile.html',
                           sellers=sellers)
  else:
    flash('You are not allowed to view the marketplace','error')
    return redirect(url_for('dashboard'))
  

"""

The customer can decide to search for a skill or a specific talent.
This route will facilitate just that.
This route will get the q parameter from url (User request from marketplace search bar)
We will create the logic to allow skill or talent to be returned.


"""    
  
@app.route('/search', methods=['GET'])
def search_sellers():
    search_query = request.args.get('q')  # Get the search query from the request
    page = request.args.get('page', 1, type=int)

    if not search_query:
        return jsonify({'error': 'No search query provided'}), 400

    # Perform the search based on seller names or skills
    sellers = Seller.query.join(Users).filter(
        or_(Users.firstname.ilike(f'%{search_query}%'),
            Users.lastname.ilike(f'%{search_query}%'),
            Seller.skill.ilike(f'%{search_query}%'))
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
    
    
@app.route('/review/<seller_id>', methods=['POST'])
@login_required
def review(seller_id):
    if request.method == 'POST':
        if current_user.role != 'customer':
            return jsonify({'error': 'Only customers can submit reviews'}), 403

        # Extract data from the request
        data = request.json  # Assuming JSON data is sent in the request body

        # Example data extraction
        rating = data.get('rating')
        text = data.get('text')

        # Validate the data (e.g., check if all required fields are present)

        # Save the review to the database
        new_review = Ratings(
            seller_id=seller_id,
            customer_id=current_user.id,
            rating=rating,
            text=text
        )
        db.session.add(new_review)
        db.session.commit()

        return jsonify({'message': 'Review submitted successfully'}), 200
    else:
        return jsonify({'error': 'Only POST requests are allowed'}), 405