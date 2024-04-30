from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from app.models import User, SellerProfile, ClientProfile, Listing, Application, Job, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin route for managing users
@admin_bp.route('/users')
# @login_required
def admin_users():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)

# Other admin routes for managing different entities (e.g., listings, jobs, etc.)