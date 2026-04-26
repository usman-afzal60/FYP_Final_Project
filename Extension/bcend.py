import email
import os
import re
import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import string
from collections import Counter
import random
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
CORS(app)

def get_saved_token():
    try:
        with open('tokens.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return row['access_token']
    except FileNotFoundError:
        return None

def analyze_eml(raw_email):
    eml = email.message_from_bytes(raw_email)


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


# def create_eml(email):
#     if not email or not email['payload'] or not email['payload']['headers']:
#         print(f"Invalid email object: {email}")
#         return None

#     subject = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'Subject')
#     from_ = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'From')
#     to = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'To')
#     date = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'Date')
#     content_type = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'Content-Type')

#     eml_content = f"Subject: {subject}\r\nFrom: {from_}\r\nTo: {to}\r\nDate: {date}\r\nContent-Type: {content_type}\r\n\r\n{email['snippet']}"
#     return eml_content

def save_token_to_csv(token):
    with open('tokens.csv', 'w', newline='') as csvfile:
        fieldnames = ['access_token']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'access_token': token})


# endpoint for receiving the OAuth token
@app.route('/token', methods=['POST'])
def receive_token():
    data = request.get_json()

    if data and 'token' in data:
        token = data['token']
        print(f"Token received: {token}")  # Add this line to print the token
        save_token_to_csv(token)
        return 'Token received.', 200
    else:
        return 'No token received.', 400


# @app.route('/upload', methods=['POST'])
# def upload():
#     data = request.get_json()

#     if data and 'email_id' in data:
#         email_id = data['email_id']

#         # Get the OAuth token from the saved location
#         token = get_saved_token()

#         if not token:
#             return 'Token not found.', 400

#         # Create credentials object from the OAuth token
#         credentials = Credentials(token)
        
#         try:
#             # Fetch the email using Gmail API
#             email = get_email_details(credentials, email_id)

#             if email:
#                 eml = create_eml(email)

#                 if eml:
#                     with open(f'{email_id}.eml', 'w') as f:
#                         f.write(eml)

#                     # Analyze the EML file here, and store the result in the "analysis_result" variable
#                     # ...
#                     analysis_result = {
#                         "email_id": email_id,
#                         "status": "safe"  # Replace this with the actual analysis result (e.g., "phishing" or "safe")
#                     }

#                     return jsonify(analysis_result), 200
#                 else:
#                     return 'Failed to create EML.', 400
#             else:
#                 return 'Failed to fetch email.', 400
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return 'An error occurred while processing the email.', 500
#     else:
#         return 'No email ID received.', 400

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()

    if data and 'email_id' in data:
        email_id = data['email_id']

        token = get_saved_token()

        credentials = Credentials(token)

        email = get_email_details(credentials, email_id)

        if not email:
            return 'Failed to fetch email.', 400

        # Call the analyze_eml function with the email object
        analysis_results = analyze_eml(email)

        # Analyze the email, and store the result in the "analysis_result" variable
        analysis_result = {
            "email_id": email_id,
            "status": "safe",  # Replace this with the actual analysis result (e.g., "phishing" or "safe")
            "analysis": analysis_results
        }

        return jsonify(analysis_result), 200
    else:
        return 'No email ID received.', 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
