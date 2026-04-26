import asyncio
import csv
import base64
from collections import Counter
import os
import json
import re
from urllib.parse import urlparse
import aiohttp
import email
from bs4 import BeautifulSoup
import string
from quart import Quart, request, jsonify, Response
import httpx
from quart_cors import cors
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import jwt
import functools
import datetime
from quart import abort
import os
from datetime import datetime
from quart import Quart, request, jsonify, send_from_directory, url_for,send_file, make_response, Response, copy_current_websocket_context


import url_extractor as ue
import structure_extractor as se
import text_extractor as te
import pdf_creator as pc
import json_creator as jc
import standard_details_ext as sde
import pandas as pd
import numpy as np
import torch
import tensorflow as tf
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer, BertModel
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
# from xgboost import XGBClassifier
import joblib
import pickle
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, Dense, TimeDistributed
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder


react_app_url = "http://localhost:3000"

if not os.path.exists('reports'):
    os.makedirs('reports')


app = Quart(__name__)
app = cors(app, allow_origin="*")


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def get_email_details(credentials, email_id):
    async with aiohttp.ClientSession() as session:
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}?format=raw"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = await fetch(session, url, headers)
        raw_email = base64.urlsafe_b64decode(response['raw'].encode('ASCII'))
        eml = email.message_from_bytes(raw_email)
        return eml

def get_json_report(filename):
    with open("/root/pyserver/jsonreports/"+filename,"r") as file:  
        return json.load(file)



def create_reports(data):
    pc.create_pdf_report(data)
    jc.create_json_report(data)
    print("Reports Created Successfully.")
# create_reports()

# Load the models
text_moudule_loaded = joblib.load("AI-models/text_module.joblib")
url_module_loaded = load_model("AI-models/url_module.h5")
structure_module_loaded = joblib.load("AI-models/structure_module.joblib")
meta_module_loaded = joblib.load("AI-models/meta_module.joblib")

# Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased').eval()

# Load the tokenizer using pickle
with open("AI-models/tokenizer_url.pickle", "rb") as handle:
    tokenizer_url = pickle.load(handle)
 

async def analyze_eml(email_id,eml):
    urls = ue.url_extractor(eml)

    structure = se.extract_str_attr(eml)

    texts = te.extract_text_sections(eml)

    # Prediction data preprocessing for structure module
    pred_data_S_module = pd.read_csv('new.csv')

    # Preprocess new data: transform non-numeric columns using LabelEncoder
    non_numeric_columns = pred_data_S_module.select_dtypes(include=['object']).columns
    encoders = {column: LabelEncoder() for column in non_numeric_columns}

    for column, encoder in encoders.items():
        pred_data_S_module[column] = encoder.fit_transform(pred_data_S_module[column])

    for column in non_numeric_columns:
        if column in encoders:
            encoder = encoders[column]
            # Add an additional category 'unseen' for unseen labels
            pred_data_S_module[column] = pred_data_S_module[column].map(lambda x: x if x in encoder.classes_ else 'unseen')
            
            # Extend the encoder classes to include the 'unseen' category
            encoder_classes_extended = list(encoder.classes_) + ['unseen']
            encoder.classes_ = np.array(encoder_classes_extended)
            
            pred_data_S_module[column] = encoder.transform(pred_data_S_module[column])
        else:
            # Create a new encoder for the column if it doesn't exist in the encoders dictionary
            new_encoder = LabelEncoder()
            pred_data_S_module[column] = new_encoder.fit_transform(pred_data_S_module[column])
            encoders[column] = new_encoder

    # Make sure pred_data_S_module has the same column order as X
    prediction_data_S_module = structure_module_loaded.predict(pred_data_S_module)

    # Prediction data preprocessing for URL module

    # Preprocess the input data
    def preprocess_data_U(data, tokenizer_url, max_url_length=200, num_characters=256):
        sequences = tokenizer_url.texts_to_sequences(data)
        x_data = pad_sequences(sequences, maxlen=max_url_length)
        x_data = np.expand_dims(x_data, axis=-1)  # Add the channel dimension
        x_data = x_data / float(num_characters)
        return x_data
    
    # Read URLs from a CSV file
    # csv_file_path = "url.csv"
    # df = pd.read_csv(csv_file_path)

    # Extract the URLs from the CSV file
    # test_urls = df["url"].tolist()
    test_urls = urls
    print(test_urls)  # added_new
    if len(test_urls) == 0:
        test_urls.append("www.google.com")



    # Preprocess the test URL
    pred_data_URL_module = preprocess_data_U(test_urls, tokenizer_url)

    # Prediction data preprocessing for Text module
    # Get BERT embeddings
    def get_bert_embeddings(texts, tokenizer, model):
        embeddings = []
        for text in texts:
            inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = model(**inputs)
            embeddings.append(outputs.last_hidden_state[:, 0, :].numpy())
        return np.vstack(embeddings)

    # Load the test_texts from a CSV file
    # csv_file_path = "text.csv"
    # test_df = pd.read_csv(csv_file_path)

    # Extract the test_texts
    # test_texts = test_df["text"].tolist()
    test_texts = texts
    if len(test_texts) == 0:
        test_texts.append("Hello")

    # Get the BERT embeddings for test texts
    test_embeddings = get_bert_embeddings(test_texts, tokenizer, bert_model)

    # Use the models to generate predictions for the combined Meta module
    text_module_predictions = text_moudule_loaded.predict(test_embeddings)
    url_module_predictions = url_module_loaded.predict(pred_data_URL_module)
    url_module_predictions_final = np.mean(url_module_predictions)
    print(url_module_predictions_final) #added_new
    structure_module_predictions = structure_module_loaded.predict(pred_data_S_module)

    # Combine the predictions
    combined_features = np.column_stack((text_module_predictions, url_module_predictions_final, structure_module_predictions))

    pred_meta = meta_module_loaded.predict(combined_features)
    details = sde.extract_standard_details(eml)
    rslt = ''
    score = '-1'
    if pred_meta[0] == '0':
        rslt = "Spam"
        score = 0.0
    else:
        rslt = "Ham"
        score = 1.0
    data = {
        "ID": email_id,
        "Subject": details[0] ,
        "Date": details[1],
        "Result": rslt,
        "Sender": details[2],
        "Recipient": details[3],
        "Body": details[4],
        "Score": score
    }
    create_reports(data)

    return pred_meta


@app.route('/upload', methods=['POST'])
async def upload():
    data = await request.get_json()

    if data and 'email_id' in data and 'token' in data:
        email_id = data['email_id']
        token = data['token']

        credentials = Credentials(token)

        email = await get_email_details(credentials, email_id)

        if not email:
            return 'Failed to fetch email.', 400

        # Call the analyze_eml function with the email object
        analysis_results = await analyze_eml(email_id,email)

        report_path = f"reports/{email_id}.pdf"
        # await create_pdf_report(analysis_results)


        # Analyze the EML file here, and store the result in the "analysis_result" variable
        # ...
        

        return "Sent!", 200
    else:
        return 'No email ID and/or token received.', 400

async def fetch_token_info(session, token):
    async with session.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={token}') as response:
        return await response.json()


# this code sends the json reports to the front end

@app.route('/json_reports', methods=['GET'])
def get_json_reports():
    json_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsonreports')
    reports = []

    # Iterate over the JSON files in the directory
    for filename in os.listdir(json_reports_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(json_reports_dir, filename)

            # Load the JSON data from the file and append it to the reports list
            with open(filepath) as f:
                data = json.load(f)
                reports.append(data)

    return jsonify(reports), 200


@app.route('/generate-report/<id>', methods=['GET'])
async def generate_report(id):
    # The reports directory already contains the files named with their ids
    report_path = f'reports/{id}.pdf'

    if os.path.exists(report_path):
        return await send_file(report_path, attachment_filename=f'{id}.pdf', as_attachment=True, mimetype='application/pdf')
    else:
        return {"error": "Report not found"}, 404

@app.route('/view-report/<id>', methods=['GET'])
async def view_report(id):
    # The reports directory already contains the files named with their ids
    report_path = f'reports/{id}.pdf'

    if os.path.exists(report_path):
        return await send_file(report_path, mimetype='application/pdf')
    else:
        return {"error": "Report not found"}, 404


@app.route('/reports', methods=['POST'])
async def protected_route():
    data = await request.get_json()

    if data and 'token' in data:
        token = data['token']
        print(f"Token: {token}")

        async with aiohttp.ClientSession() as session:
            token_info = await fetch_token_info(session, token)
            print(f"Token info: {token_info}")

            if 'error' in token_info:
                return jsonify({"error": "Unauthorized"}), 401

        # Your route logic here
        return jsonify({"message": "You have access to this protected route!"}), 200
    else:
        return jsonify({"error": "Unauthorized"}), 401

