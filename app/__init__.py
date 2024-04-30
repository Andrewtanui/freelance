from flask import (Flask, request)
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')


from . import (auth,
                 views,
                 seller, 
                 customer,
                 search_marketplace,
                 models,
                 errors,
                 jobs,
                 apply_listings,
                 listings,
                 messages,
                 admin,
                 notifications)



from flask import stream_with_context, Response
import time

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            # Send a "keepalive" event every 30 seconds to keep the connection alive
            yield f"data: {{'event': 'keepalive'}}\n\n"
            time.sleep(30)

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")