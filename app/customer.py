from app import app
from flask import render_template, flash, url_for, redirect
from flask_login import login_required,current_user
from .models import Seller

  
@app.route('/marketplace')
@login_required
def marketplace():
  if current_user.role == 'customer':
    sellers = Seller.query.all()
    return render_template('marketplace.html',
                           sellers=sellers)
  else:
    flash('You are not allowed to view the marketplace','error')
    return redirect(url_for('dashboard'))