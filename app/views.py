"""
This file only holds the static routes such us the landing page
Not alot of attention is required in this file


"""

from app import app
from flask import render_template

@app.route('/')
def home():
  return render_template('index.html')
