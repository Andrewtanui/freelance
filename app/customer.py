from app import app
from flask import render_template


  
@app.route('/marketplace')
def marketplace():
  return render_template('dashboard.html')