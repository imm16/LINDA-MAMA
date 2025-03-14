from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend to fetch from backend

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Chat Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Fetch messages by category
@app.route('/get_messages/<category>', methods=['GET'])
def get_messages(category):
    messages = Message.query.filter_by(category=category).order_by(Message.timestamp).all()
    return jsonify([{
        "username": msg.username,
        "content": msg.content,
        "timestamp": msg.timestamp.strftime("%I:%M %p"),
        "category": msg.category  # Make sure category is included
    } for msg in messages])


# Save a new message
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    new_message = Message(username=data["username"], category=data["category"], content=data["content"])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({"status": "Message sent!"})

@app.route("/status")
def status():
    return jsonify({"status": "online"}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database is created
    app.run(debug=True)

@app.route('/clear_messages', methods=['DELETE'])
def clear_messages():
    try:
        db.session.query(Message).delete()  # Delete all messages
        db.session.commit()
        
        # Confirm database is empty
        remaining_messages = Message.query.all()
        if not remaining_messages:
            return jsonify({"message": "All messages have been cleared."}), 200
        else:
            return jsonify({"error": "Some messages were not deleted."}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



