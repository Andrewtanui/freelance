from app import app
from flask import (request,
                   redirect,
                   render_template,
                   url_for)

from .models import db, Listing

from flask_login import current_user

@app.route('/listing', methods=['POST'])
def listing():

  # Get data from form
  title = request.form.get('title')
  description = request.form.get('description')
  budget = request.form.get('budget')
  deadline = request.form.get('deadline')

  # Check if current user is a client
  if current_user.role != 'client':
    return 'Unauthorized', 401

  # Create new Listing object
  new_listing = Listing(
    title=title, 
    description=description,
    budget=budget,
    deadline=deadline,
    client=current_user
  )

  # Save to database
  db.session.add(new_listing)
  db.session.commit()

  # Redirect to client profile
  return redirect(url_for('client_profile', client_id=current_user.id)), 201

  

# Get a specific listing 
@app.route('/listings/<int:id>')
def viewListing():
    pass
#TODO Query for listing with id
#TODO Return listing JSON


# Update a listing
@app.route('/listings/<int:id>', methods=['PUT'])
def updateListing():
  pass
    # Get data from form 
    # Query for listing
    # Update listing fields
    # db.commit()
    # Return 200 response

# Delete a listing
@app.route('/listings/<int:id>', methods=['DELETE'])  
def delete_listing(id):
  pass
  # Query for listing
  # db.delete(listing)
  # db.commit()
  # Return 204 response    