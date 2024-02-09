from app import app
from flask import render_template


  
@app.route('/marketplace/search/keyword/<query>')
def search_marketplace():
  return render_template('dashboard.html')