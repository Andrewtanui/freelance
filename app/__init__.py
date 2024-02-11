from flask import (Flask, request)
from flask_socketio import SocketIO

app = Flask(__name__)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')

socketio = SocketIO(app)

from . import (auth,
                 views,
                 seller, 
                 customer,
                 search_marketplace,
                 models)


# SocketIO event handler for connecting clients
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")