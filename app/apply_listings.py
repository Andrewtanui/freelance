from app import app
from app.models import Application, Listing, db
from flask import jsonify, request

# Apply for a listing
@app.route('/listings/<int:listing_id>/apply', methods=['POST'])
def apply_to_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    data = request.get_json()
    cover_letter = data.get('cover_letter')

    if not cover_letter:
        return jsonify({'error': 'Cover letter is required'}), 400

    freelancer_id = request.args.get('freelancer_id')
    if not freelancer_id:
        return jsonify({'error': 'Freelancer ID is required'}), 400

    application = Application(cover_letter=cover_letter, freelancer_id=freelancer_id, listing=listing)
    db.session.add(application)
    db.session.commit()

    return jsonify({'message': 'Application submitted successfully'}), 201

# Get applications for a listing
@app.route('/listings/<listing_id>/applications')
def get_listing_applications(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    applications = listing.applications

    return jsonify([{
        'id': application.id,
        'cover_letter': application.cover_letter,
        'freelancer': application.freelancer.get_full_name()
    } for application in applications])

# Approve/reject application
@app.route('/applications/<id>', methods=['PUT'])
def update_application(id):
    application = Application.query.get_or_404(id)

    data = request.get_json()
    status = data.get('status')

    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    application.status = status
    db.session.commit()

    return jsonify({'message': 'Application status updated successfully'}), 200