import pandas as pd
import numpy as np
import torch
import tensorflow as tf
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer, BertModel
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from xgboost import XGBClassifier
import joblib
import pickle
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, Dense, TimeDistributed
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder


import url_extractor as ue
import structure_extractor as se
import text_extractor as te
import pdf_creator as pc
import json_creator as jc
import standard_details_ext as sde

urls = ue.url_extractor(eml)
print(urls)

structure = se.extract_str_attr(eml)
# ,len(structure[0]),len(structure[1])
print(structure)

texts = te.extract_text_sections(eml)
print(texts)

# Load the models
text_moudule_loaded = joblib.load("AI-models/text_module.joblib")
url_module_loaded = load_model("AI-models/url_module.h5")
structure_module_loaded = joblib.load("AI-models/structure_module.joblib")
meta_module_loaded = joblib.load("AI-models/meta_module.joblib")

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

# Load the tokenizer using pickle
with open("tokenizer_url.pickle", "rb") as handle:
    tokenizer_url = pickle.load(handle)

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
# Preprocess the test URL
pred_data_URL_module = preprocess_data_U(test_urls, tokenizer_url)

# Prediction data preprocessing for Text module

# Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased').eval()

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

# Get the BERT embeddings for test texts
test_embeddings = get_bert_embeddings(test_texts, tokenizer, bert_model)

# Use the models to generate predictions for the combined Meta module
text_module_predictions = text_moudule_loaded.predict(test_embeddings)
url_module_predictions = url_module_loaded.predict(pred_data_URL_module)
structure_module_predictions = structure_module_loaded.predict(pred_data_S_module)

# Combine the predictions
combined_features = np.column_stack((text_module_predictions, url_module_predictions, structure_module_predictions))

pred_meta = meta_module_loaded.predict(combined_features)
print(pred_meta)