
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


def create_job():
    listing_id = request.form.get('listing_id')
    freelancer_id = request.form.get('freelancer_id')
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')

    listing = Listing.query.get(listing_id)
    if not listing or listing.client_id != current_user.id:
        flash('You are not authorized to create a job for this listing.', 'danger')
        return redirect(url_for('marketplace'))

    new_job = Job(
        title=job_title,
        description=job_description,
        client_id=current_user.id,
        freelancer_id=freelancer_id,
        listing_id=listing_id
    )

    db.session.add(new_job)
    db.session.commit()

    flash('Job created successfully.', 'success')
    return redirect(url_for('sellers/view_job', job_id=new_job.id))

@app.route('/jobs/<job_id>/complete', methods=['POST'])
@login_required
def complete_job(job_id):
    job = Job.query.get_or_404(job_id)

    if job.client_id != current_user.id:
        flash('You are not authorized to complete this job.', 'danger')
        return redirect(url_for('marketplace'))

    # Check if all deliverables are approved
    unapproved_deliverables = Deliverable.query.filter_by(job_id=job_id, approved=False).count()
    if unapproved_deliverables > 0:
        flash('Cannot complete the job until all deliverables are approved.', 'warning')
        return redirect(url_for('view_job', job_id=job_id))

    # Mark the job as completed
    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    db.session.commit()

    # Initiate payment process
    payment_amount = job.listing.budget
    # Handle payment process here (e.g., integrate with a payment gateway)

    flash('Job completed successfully. Payment processed.', 'success')
    return redirect(url_for('view_job', job_id=job_id))

@app.route('/jobs/<job_id>/deliverables', methods=['POST'])
@login_required
def manage_deliverables(job_id):
    job = Job.query.get_or_404(job_id)

    if job.client_id != current_user.id:
        flash('You are not authorized to manage deliverables for this job.', 'danger')
        return redirect(url_for('marketplace'))

    deliverable_id = request.form.get('deliverable_id')
    action = request.form.get('action')

    if action == 'approve':
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        deliverable.approved = True
        db.session.commit()
        flash('Deliverable approved successfully.', 'success')
    elif action == 'request_revision':
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        deliverable.approved = False
        db.session.commit()
        flash('Revision requested for the deliverable.', 'info')

    return redirect(url_for('sellers/view_job', job_id=job_id))


@app.route('/jobs/<job_id>', methods=['GET', 'POST'])
@login_required
def view_job(job_id):
    job = Job.query.get_or_404(job_id)

    if current_user.id != job.freelancer_id:
        flash('You are not authorized to view this job.', 'danger')
        return redirect(url_for('marketplace'))

    if request.method == 'POST':
        # Handle deliverable upload
        deliverable_title = request.form.get('deliverable_title')
        deliverable_description = request.form.get('deliverable_description')
        deliverable_file = request.files.get('deliverable_file')

        if deliverable_file:
            # Save the uploaded file
            deliverable_file_path = save_file(deliverable_file)

            new_deliverable = Deliverable(
                title=deliverable_title,
                description=deliverable_description,
                file_path=deliverable_file_path,
                job_id=job_id
            )

            db.session.add(new_deliverable)
            db.session.commit()

            flash('Deliverable uploaded successfully.', 'success')

    deliverables = Deliverable.query.filter_by(job_id=job_id).all()
    return render_template('sellers/view_job.html', job=job, deliverables=deliverables)








