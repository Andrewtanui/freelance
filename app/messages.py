from flask import request, redirect, url_for, render_template, flash
from app import app
from app.models import Message, User, db
from datetime import datetime

@app.route('/send_message', methods=['POST'])
def send_message():
    sender_id = request.form.get('sender_id')
    recipient_id = request.form.get('recipient_id')
    body = request.form.get('body')

    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        flash('Invalid sender or recipient ID', 'error')
        return redirect(url_for('send_message_form'))

    message = Message(body=body, sent_at=datetime.now(), sender=sender, recipient=recipient)
    db.session.add(message)
    db.session.commit()

    flash('Message sent successfully', 'success')
    return redirect(url_for('inbox'))
"""
@app.route('/messages/<string:sender_id>/<string:recipient_id>', methods=['GET'])
def get_messages(sender_id, recipient_id):
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        flash('Invalid sender or recipient ID', 'error')
        return redirect(url_for('inbox'))

    messages = Message.query.filter((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id) |
                                    (Message.sender_id == recipient_id) & (Message.recipient_id == sender_id)).all()

    return render_template('messages.html', messages=messages, sender=sender, recipient=recipient)

"""
@app.route('/messages/<string:message_id>/read', methods=['POST'])
def read_message(message_id):
    message = Message.query.get(message_id)

    if not message:
        flash('Message not found', 'error')
        return redirect(url_for('inbox'))

    message.is_read = True
    db.session.commit()

    flash('Message marked as read', 'success')
    return redirect(url_for('inbox'))