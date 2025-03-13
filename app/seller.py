from app import app
from flask import render_template


  
@app.route('/seller/dashboard')
def seller_dashboard():
  return render_template('dashboard.html')


@app.route('/orders')
def orders():
  return render_template('Orders.html')


@app.route('/seller/profile')
def seller_profile():
  return render_template('profile.html')