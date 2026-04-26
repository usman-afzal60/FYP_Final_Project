from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import email
import os
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import string
from collections import Counter
import base64

app = Flask(__name__)
CORS(app)

def save_token_to_csv(token):
    with open('tokens.csv', 'w', newline='') as csvfile:
        fieldnames = ['access_token']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'access_token': token})

def get_saved_token():
    try:
        with open('tokens.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return row['access_token']
    except FileNotFoundError:
        return None

def get_email_details(credentials, email_id):
    service = build('gmail', 'v1', credentials=credentials)
    try:
        message = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
        raw_email = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        eml = email.message_from_bytes(raw_email)
        return eml
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

def analyze_eml(eml):
    plain = 0
    html = 0
    other_text = -1
    application = 0
    image = 0

    for part in eml.walk():
        content_type = part.get_content_type()

        if content_type == "text/plain":
            plain += 1
        if content_type == "text/html":
            html += 1
            html_text = part.get_payload(decode=True)
            html_text_length = len(html_text)

        if content_type.startswith('text/'):
            other_text += 1

        if content_type.startswith('application/'):
            application += 1

        if content_type.startswith('image/'):
            image += 1

    results = {
        "plain_sections": plain,
        "html_sections": html,
        "application_sections": application,
        "image_sections": image,
        "plain_to_text_ratio": plain / other_text,
        "html_text_length": html_text_length
    }

    return results

# endpoint for receiving the OAuth token
@app.route('/token', methods=['POST'])
def receive_token():
    data = request.get_json()

    if data and 'token' in data:
        token = data['token']
        print(f"Received token: {token}")  # Add this line
        save_token_to_csv(token)
        return 'Token received.', 200
    else:
        return 'No token received.', 400




@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()

    if data and 'email_id' in data:
        email_id = data['email_id']

        # Get the OAuth token from the saved location
        token = get_saved_token()

        credentials = Credentials(token)

        email = get_email_details(credentials, email_id)

        if not email:
            return 'Failed to fetch email.', 400


        # Call the analyze_eml function with the email object
        analysis_results = analyze_eml(email)
        print(analysis_results)

        # Analyze the EML file here, and store the result in the "analysis_result" variable
        # ...
        analysis_result = {
            "email_id": email_id,
            "status": "safe"  # Replace this with the actual analysis result (e.g., "phishing" or "safe")
        }

        return jsonify(analysis_result), 200
    else:
        return 'No email ID received.', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80) # 443  ssl_context=('certs/cert.pem', 'certs/key.pem')