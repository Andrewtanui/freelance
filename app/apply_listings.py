from app import app

# Apply for a listing
@app.route('/listings/<int:listing_id>/apply', methods=['POST'])
def apply_to_listing(listing_id):
  pass
  # Get listing
  # Create new Application object
  # Save to db
  # Return 201 response

# Get applications for a listing
@app.route('/listings/<int:listing_id>/applications')
def get_listing_applications(listing_id):
  pass
  # Query for applications with listing_id
  # Return JSON of applications

# Approve/reject application
@app.route('/applications/<int:id>', methods=['PUT']) 
def update_application(id):
  pass
  # Get data from form
  # Query for application
  # Update status field
  # Return 200 response