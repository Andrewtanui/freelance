from app import app
from flask import request, redirect, render_template, url_for
from .models import db, Listing
from flask_login import current_user
from datetime import datetime

@app.route('/listing', methods=['GET', 'POST'])
def listing():
    if request.method == "POST":
        # Get data from form
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        
        # Convert deadline string to datetime object
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        # Check if current user is a client
        if current_user.role != 'customer':
            return 'Unauthorized', 401

        # Create new Listing object
        listing = Listing(
            title=title,
            description=description,
            budget=budget,
            deadline=deadline,
            client_id=current_user.id
        )

        # Save to database
        db.session.add(listing)
        db.session.commit()

        return redirect(url_for('marketplace')), 201
    return render_template('listings.html')

@app.route('/listings/<int:id>')
def viewListing(id):
    listing = Listing.query.get_or_404(id)
    return render_template('listing.html', listing=listing)

# Update a listing
@app.route('/listings/<int:id>', methods=['PUT'])
def updateListing(id):
    listing = Listing.query.get_or_404(id)

    # Check if the current user is authorized to update this listing
    if listing.client_id != current_user.id:
        return 'Unauthorized', 401

    # Get data from form
    title = request.form.get('title')
    description = request.form.get('description')
    budget = request.form.get('budget')
    deadline = request.form.get('deadline')

    # Update listing object
    listing.title = title or listing.title
    listing.description = description or listing.description
    listing.budget = budget or listing.budget
    listing.deadline = deadline or listing.deadline

    # Save to database
    db.session.commit()

    return redirect(url_for('viewListing', id=listing.id))

