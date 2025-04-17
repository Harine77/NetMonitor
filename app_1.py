from flask import Flask, jsonify
from flask_cors import CORS
import threading
import scapy.all as scapy
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import networkx as nx
import time
#(myenv) C:\HAR\network_monitoring>python main.py

app = Flask(__name__)
CORS(app)  # Enable frontend access

captured_packets = []
model_trained = False
model = None

def packet_callback(packet):
    if scapy.IP in packet:
        src_ip = packet[scapy.IP].src
        dst_ip = packet[scapy.IP].dst
        proto = packet[scapy.IP].proto
        length = len(packet)
        timestamp = time.time()
        captured_packets.append([timestamp, src_ip, dst_ip, proto, length])
        if len(captured_packets) > 1000:
            captured_packets.pop(0)

def start_sniffing():
    scapy.sniff(prn=packet_callback, store=False, count=10)

@app.route('/start-monitoring', methods=['GET'])
def start_monitoring():
    threading.Thread(target=start_sniffing, daemon=True).start()
    return jsonify({"message": "Traffic monitoring started!"})

@app.route('/get-traffic', methods=['GET'])
def get_traffic():
    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])
    return jsonify(df.to_dict(orient="records"))

def process_data():
    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])
    encoder = LabelEncoder()
    df['Source IP'] = encoder.fit_transform(df['Source IP'])
    df['Destination IP'] = encoder.fit_transform(df['Destination IP'])
    scaler = MinMaxScaler()
    df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']] = scaler.fit_transform(df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']])
    return df

def create_sequences(data, seq_length=10):
    sequences, targets = [], []
    for i in range(len(data) - seq_length):
        sequences.append(data.iloc[i:i + seq_length].values)
        targets.append(data.iloc[i + seq_length]['Length'])
    return np.array(sequences), np.array(targets)

def train_model():
    global model, model_trained
    df = process_data()
    if len(df) < 20:
        return None
    seq_length = 10
    X, y = create_sequences(df, seq_length)
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
    model_trained = True
    return model

@app.route('/train-model', methods=['GET'])
def api_train_model():
    if not model_trained:
        train_model()
        return jsonify({"message": "Model trained successfully"})
    return jsonify({"message": "Model already trained"})

@app.route('/predict-traffic', methods=['GET'])
def predict_traffic():
    if not model_trained or len(captured_packets) < 10:
        return jsonify({"message": "Not enough data"})
    df = process_data()
    seq_length = 10
    X, _ = create_sequences(df, seq_length)
    predicted_traffic = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))[0][0]
    return jsonify({"predicted_traffic": predicted_traffic})

if __name__ == '__main__':
    app.run(debug=True)
