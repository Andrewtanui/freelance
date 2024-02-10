from app import app
from flask import render_template


  
@app.route('/dashboard')
def dashboard():
  return render_template('dashboard.html')


@app.route('/orders')
def orders():
  return render_template('Orders.html')


@app.route('/profile')
def profile():
  return render_template('profile.html')