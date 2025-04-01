from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from pyngrok import ngrok

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get Twilio credentials
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# validator = RequestValidator(TWILIO_AUTH_TOKEN)

# Patient database (in a real app, this would be a database)
# For this example, we'll use a simple JSON file
PATIENT_DB_FILE = "patient_responses.json"

def load_patient_db():
    """Load patient database from JSON file."""
    try:
        if os.path.exists(PATIENT_DB_FILE):
            with open(PATIENT_DB_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading patient database: {e}")
        return {}

def save_patient_db(db):
    """Save patient database to JSON file."""
    try:
        with open(PATIENT_DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving patient database: {e}")

def save_patient_response(phone_number, message):
    """Save a patient's response."""
    db = load_patient_db()
    
    # If this is a new phone number, create a new entry
    if phone_number not in db:
        db[phone_number] = {
            "responses": [],
            "processed": False
        }
    
    # Add the new response
    db[phone_number]["responses"].append({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })
    
    # Set processed to False since this is a new response
    db[phone_number]["processed"] = False
    
    # Save the updated database
    save_patient_db(db)
    
    logger.info(f"Saved response from {phone_number}")

@app.route('/sms', methods=['POST'])
def sms_webhook():
    """Handle incoming SMS messages."""
    # Log all request details
    logger.info(f"Received webhook request from: {request.remote_addr}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Form data: {dict(request.form)}")
    
    # VALIDATION REMOVED FOR TESTING
    # No validation check here
    
    # Get the message content and sender's phone number
    incoming_message = request.form.get('Body', '')
    from_number = request.form.get('From', '')
    
    logger.info(f"Received message from {from_number}: {incoming_message}")
    
    # Save the patient's response
    save_patient_response(from_number, incoming_message)
    
    # Create a response
    resp = MessagingResponse()
    resp.message("Thank you for your response. A dental professional will review your information shortly.")
    
    return str(resp)

@app.route('/responses', methods=['GET'])
def get_responses():
    """API endpoint to get all patient responses."""
    # In a production app, you'd want to add authentication here
    db = load_patient_db()
    return db

@app.route('/responses/<phone_number>', methods=['GET'])
def get_patient_responses(phone_number):
    """API endpoint to get responses for a specific patient."""
    # In a production app, you'd want to add authentication here
    db = load_patient_db()
    if phone_number in db:
        return db[phone_number]
    return {"error": "Patient not found"}, 404

@app.route('/responses/<phone_number>/mark-processed', methods=['POST'])
def mark_processed(phone_number):
    """API endpoint to mark a patient's responses as processed."""
    # In a production app, you'd want to add authentication here
    db = load_patient_db()
    if phone_number in db:
        db[phone_number]["processed"] = True
        save_patient_db(db)
        return {"status": "success"}
    return {"error": "Patient not found"}, 404

@app.route('/test-webhook', methods=['GET', 'POST'])
def test_webhook():
    """Simple test endpoint to verify the webhook is accessible."""
    # Log the request
    logger.info(f"Test webhook called with method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Args: {dict(request.args)}")
    logger.info(f"Form: {dict(request.form)}")
    
    # Return a simple response
    return {
        "status": "success",
        "message": "Webhook test successful",
        "method": request.method,
        "time": datetime.now().isoformat()
    }

@app.route('/simple-test', methods=['GET', 'POST'])
def simple_test():
    """Simplest possible test endpoint."""
    method = request.method
    
    # Log the request
    print(f"Simple test endpoint called with method: {method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Args: {dict(request.args)}")
    print(f"Form: {dict(request.form)}")
    
    # Return a plain text response
    return f"Hello! This is a simple test. Method: {method}, Time: {datetime.now().isoformat()}"

if __name__ == '__main__':
    # Start ngrok tunnel
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")
    
    # Run the Flask app on port 5000
    app.run(debug=False, host='0.0.0.0', port=5000)