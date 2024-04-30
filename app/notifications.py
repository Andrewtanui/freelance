from flask import render_template, flash, url_for, redirect, request, session
from flask_login import login_required
from .models import  User, db, Message
from functools import cache

# notifications.py

from flask_socketio import emit, join_room, leave_room
from app import socketio, app
from datetime import datetime
# Dictionary to store connected clients
connected_clients = {}

def send_notification(recipient_id, event, data):
    if recipient_id in connected_clients:
        emit('notification', {'event': event, 'data': data}, room=connected_clients[recipient_id])

def register_client(client_id, recipient_id):
    connected_clients[recipient_id] = client_id

def unregister_client(recipient_id):
    if recipient_id in connected_clients:
        del connected_clients[recipient_id]

@socketio.on('connect')
def on_connect():
    user_id = session.get('user_id')
    if user_id:
        register_client(request.sid, user_id)
        join_room(user_id)

@socketio.on('disconnect')
def on_disconnect():
    user_id = session.get('user_id')
    if user_id:
        unregister_client(user_id)
        leave_room(user_id)

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    body = data.get('body')

    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if sender and recipient:
        message = Message(body=body, sent_at=datetime.now(), sender=sender, recipient=recipient)
        db.session.add(message)
        db.session.commit()

        # Emit the new message to the sender and recipient rooms
        emit('new_message', {'message': message.body, 'sender_name': sender.get_full_name()}, room=sender_id)
        emit('new_message', {'message': message.body, 'sender_name': sender.get_full_name()}, room=recipient_id)

@app.route('/messages/<string:sender_id>/<string:recipient_id>', methods=['GET'])
@login_required
def get_messages(sender_id, recipient_id):
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        flash('Invalid sender or recipient ID', 'error')
        return redirect(url_for('inbox'))

    messages = Message.query.filter((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id) |
                                    (Message.sender_id == recipient_id) & (Message.recipient_id == sender_id)).all()

    return render_template('messages.html', messages=messages, sender=sender, recipient=recipient)