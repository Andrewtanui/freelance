from datetime import datetime, timedelta
from sqlalchemy import func
from app import app
from app.models import *
from flask import render_template

def get_new_users_count(start_date, end_date):
    return User.query.filter(User.created_at >= start_date, User.created_at <= end_date).count()

def get_new_freelancers_count(start_date, end_date):
    return SellerProfile.query.filter(SellerProfile.created_at >= start_date, SellerProfile.created_at <= end_date).count()

def get_completed_jobs_count(start_date, end_date):
    return Job.query.filter(Job.status == 'completed', Job.completed_at >= start_date, Job.completed_at <= end_date).count()

def get_total_earnings(start_date, end_date):
    return db.session.query(func.sum(Payment.amount)).join(Job).filter(Payment.paid_at >= start_date, Payment.paid_at <= end_date).scalar() or 0

def get_top_freelancers(start_date, end_date, limit=10):
    top_freelancers = (
        db.session.query(User.id, User.firstname, User.lastname, func.count(Job.id).label('job_count'))
        .join(User.jobs_as_freelancer)
        .join(Job.payments)
        .filter(Job.completed_at >= start_date, Job.completed_at <= end_date)
        .group_by(User.id)
        .order_by(func.count(Job.id).desc())
        .limit(limit)
        .all()
    )
    return top_freelancers

def get_average_rating(start_date, end_date):
    avg_rating = (
        db.session.query(func.avg(Rating.rating).label('avg_rating'))
        .join(Rating.seller)
        .filter(Rating.created_at >= start_date, Rating.created_at <= end_date)
        .scalar()
    )
    return avg_rating or 0

"""
@app.route('/analytics')
def analytics_dashboard():
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Get analytics for the last week
    new_users_last_week = get_new_users_count(last_week, today)
    new_freelancers_last_week = get_new_freelancers_count(last_week, today)
    completed_jobs_last_week = get_completed_jobs_count(last_week, today)
    earnings_last_week = get_total_earnings(last_week, today)
    top_freelancers_last_week = get_top_freelancers(last_week, today)
    avg_rating_last_week = get_average_rating(last_week, today)

    # Get analytics for the last month
    new_users_last_month = get_new_users_count(last_month, today)
    new_freelancers_last_month = get_new_freelancers_count(last_month, today)
    completed_jobs_last_month = get_completed_jobs_count(last_month, today)
    earnings_last_month = get_total_earnings(last_month, today)
    top_freelancers_last_month = get_top_freelancers(last_month, today)
    avg_rating_last_month = get_average_rating(last_month, today)

    return render_template('analytics.html', **locals())

"""
from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from .models import SellerProfile, Rating, Deliverable, Job


def get_seller_profile(user_id):
    return SellerProfile.query.filter_by(user_id=user_id).first()

def get_rating_stats(seller_id):
    if seller_id:
        ratings = Rating.query.filter_by(seller_id=seller_id).all()
        total_ratings = len(ratings)
        if total_ratings > 0:
            average_rating = sum(rating.rating for rating in ratings) / total_ratings
        else:
            average_rating = 0
    else:
        total_ratings = 0
        average_rating = 0
    return total_ratings, average_rating

def get_deliverable_stats(seller_id):
    total_deliverables = Deliverable.query.join(Job).filter(Job.freelancer_id == current_user.id).count()
    approved_deliverables = Deliverable.query.join(Job).filter(Job.freelancer_id == current_user.id, Deliverable.approved == True).count()
    return total_deliverables, approved_deliverables

def get_job_stats(seller_id):
    total_jobs = Job.query.filter_by(freelancer_id=current_user.id).count()
    completed_jobs = Job.query.filter_by(freelancer_id=current_user.id, status='completed').count()
    return total_jobs, completed_jobs

def get_client_profile(user_id):
    return ClientProfile.query.filter_by(user_id=user_id).first()

def get_job_stats(client_id):
    total_jobs = Job.query.filter_by(client_id=client_id).count()
    completed_jobs = Job.query.filter_by(client_id=client_id, status='completed').count()
    return total_jobs, completed_jobs

def get_listing_stats(client_id):
    total_listings = Listing.query.filter_by(client_id=client_id).count()
    hired_listings = Job.query.join(Listing).filter(Listing.client_id == client_id, Job.status != 'open').count()
    return total_listings, hired_listings

def get_application_stats(client_id):
    total_applications = Application.query.join(Listing).filter(Listing.client_id == client_id).count()
    hired_freelancers = Job.query.filter_by(client_id=client_id).distinct(Job.freelancer_id).count()
    return total_applications, hired_freelancers