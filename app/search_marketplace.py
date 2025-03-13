from app import app
from flask import render_template


  
@app.route('/marketplace/search/keyword/<query>')
def search_marketplace(query):
  return render_template('projects_marketplace.html', search_query=query)