from app import app
from flask import render_template, flash, url_for, redirect, request, jsonify
from flask_login import login_required,current_user
from .models import SellerProfile, User, Rating, db, Job, Listing, Application
from functools import cache


@app.route('/admin/dashboard')
@login_required
@cache
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. You must be an administrator to access this page.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    freelancers = SellerProfile.query.all()
    jobs = Job.query.all()
    listings = Listing.query.all()
    applications = Application.query.all()

    return render_template('admin/dashboard.html', users=users, freelancers=freelancers, jobs=jobs, listings=listings, applications=applications)