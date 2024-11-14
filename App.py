from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Command
from flask_migrate import Migrate
import speech_recognition as sr
import pyttsx3

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# User database for recognition
user_data = {
    "0308025349802": "Sphiwe"  # Owner ID
}

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Voice command processing
@app.route('/voice-command', methods=['POST'])
def voice_command():
    data = request.get_json()
    command_text = data.get('command', '')
    user_id = data.get('user_id', '')

    user_name = user_data.get(user_id, "Unknown User")
    if user_name == "Unknown User":
        response_text = "Unrecognized ID. Please provide valid identification."
    else:
        if "hello" in command_text.lower():
            response_text = f"Hello {user_name}, how can I assist you today?"
        elif "identify" in command_text.lower():
            response_text = f"You are identified as {user_name}."
        else:
            response_text = f"Saliver heard: {command_text}"

    engine.say(response_text)
    engine.runAndWait()

    # Save the command and response to the database
    new_command = Command(command_text=command_text, response_text=response_text)
    db.session.add(new_command)
    db.session.commit()

    return jsonify({"response": response_text})

# Remote control endpoint
@app.route('/remote-control', methods=['POST'])
def remote_control():
    data = request.get_json()
    command_text = data.get('command', '').lower()
    
    if "turn on lights" in command_text:
        response_text = "Turning on the lights."
    elif "turn off lights" in command_text:
        response_text = "Turning off the lights."
    else:
        response_text = "Command not recognized for remote control."

    return jsonify({"response": response_text})

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
