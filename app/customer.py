from app import app
from flask import render_template, flash, url_for, redirect, request, jsonify
from flask_login import login_required,current_user
from .models import Seller, Users
from sqlalchemy import or_
  
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
  
  
  
@app.route('/search', methods=['GET'])
def search_sellers():
    search_query = request.args.get('q')  # Get the search query from the request

    if not search_query:
        return jsonify({'error': 'No search query provided'}), 400

    # Perform the search based on seller names or skills
    sellers = Seller.query.join(Users).filter(
        or_(Users.firstname.ilike(f'%{search_query}%'),
            Users.lastname.ilike(f'%{search_query}%'),
            Seller.skill.ilike(f'%{search_query}%'))
    ).paginate()

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
      'viewProfile.html',
      sellers = sellers,
      search_query=search_query
    ) 