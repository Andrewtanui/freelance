from app import app
from flask import render_template
from flask_login import login_required,current_user


  
@app.route('/marketplace')
@login_required
def marketplace():
  if current_user.role == 'customer':
    return render_template('dashboard.html')