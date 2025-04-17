from flask import Flask, render_template, jsonify
import scapy.all as scapy
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import time

app = Flask(__name__)

captured_packets = []
model = None  # Store trained model

# Packet Sniffing Function
def packet_callback(packet):
    global captured_packets
    if scapy.IP in packet:
        src_ip = packet[scapy.IP].src
        dst_ip = packet[scapy.IP].dst
        proto = packet[scapy.IP].proto
        length = len(packet)
        timestamp = time.time()
        captured_packets.append([timestamp, src_ip, dst_ip, proto, length])
        if len(captured_packets) > 1000:
            captured_packets.pop(0)

# API to Start Packet Sniffing
@app.route('/start_sniffing')
def start_sniffing():
    scapy.sniff(prn=packet_callback, store=False, count=10)
    return jsonify({'message': 'Packet sniffing started'})

# API to Get Captured Packets
@app.route('/get_packets')
def get_packets():
    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])
    return df.to_json(orient='records')

# API to Train the Model
@app.route('/train_model')
def train_model():
    global model
    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])
    
    if len(df) < 20:
        return jsonify({'error': 'Not enough data to train the model'})

    encoder = LabelEncoder()
    df['Source IP'] = encoder.fit_transform(df['Source IP'])
    df['Destination IP'] = encoder.fit_transform(df['Destination IP'])

    scaler = MinMaxScaler()
    df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']] = scaler.fit_transform(df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']])

    seq_length = 10
    X, y = [], []
    for i in range(len(df) - seq_length):
        X.append(df.iloc[i:i + seq_length].values)
        y.append(df.iloc[i + seq_length]['Length'])

    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(seq_length, X.shape[2])),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=16, validation_split=0.2)

    return jsonify({'message': 'Model trained successfully'})

# API for Prediction
@app.route('/predict')
def predict():
    if model is None:
        return jsonify({'error': 'Model is not trained yet'})

    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])
    
    if len(df) < 10:
        return jsonify({'error': 'Not enough data for prediction'})

    seq_length = 10
    X = np.array([df.iloc[-seq_length:].values])

    prediction = model.predict(X)[0][0]
    return jsonify({'predicted_traffic': prediction})

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
