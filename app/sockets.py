from flask_socketio import emit
from app import socketio
from app.models import Notification, Message
from datetime import datetime

@socketio.on('send_message')
def handle_send_message(data):
    # Save message to database
    message = Message(
        content=data['content'],
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        created_at=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    
    # Emit message to receiver
    emit('receive_message', {
        'content': data['content'],
        'sender_id': data['sender_id'],
        'timestamp': datetime.utcnow().isoformat()
    }, room=data['receiver_id'])

@socketio.on('submit_proposal')
def handle_submit_proposal(data):
    # Save proposal to database
    proposal = Proposal(
        project_id=data['project_id'],
        freelancer_id=data['freelancer_id'],
        cover_letter=data['cover_letter'],
        bid_amount=data['bid_amount'],
        created_at=datetime.utcnow()
    )
    db.session.add(proposal)
    db.session.commit()
    
    # Notify client
    emit('new_proposal', {
        'project_id': data['project_id'],
        'freelancer_id': data['freelancer_id'],
        'timestamp': datetime.utcnow().isoformat()
    }, room=data['client_id'])