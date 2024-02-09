from flask import (Flask)

app = Flask(__name__)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')

from . import (auth,
                 views,
                 seller, 
                 customer,
                 search_marketplace,
                 models)

