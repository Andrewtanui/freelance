from app import app

# Send a message 
@app.route('/messages', methods=['POST'])
def send_message():
  pass
  # Get data from form
  # Create Message object
  # Save to db
  # Return 201 response
  
# Get messages between two users
@app.route('/messages/<int:sender_id>/<int:recipient_id>')
def get_messages(sender_id, recipient_id):
  pass
  # Query database for messages
  # Return JSON of messages

# Mark message as read
@app.route('/messages/<int:id>', methods=['PUT'])
def read_message(id):
  pass
  # Query for message
  # Update is_read field
  # Return 200 response