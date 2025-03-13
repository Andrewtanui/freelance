from flask import (Flask)

app = Flask(__name__)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
# Provide a default secret key if the environment variable is not found
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY') or 'default_secret_key_for_development'

from . import (auth,
                 views,
                 seller, 
                 customer,
                 search_marketplace,
                 models)
