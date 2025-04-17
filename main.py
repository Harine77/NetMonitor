from flask import Flask, render_template, jsonify
import scapy.all as scapy
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import threading
import time

app = Flask(__name__)

# Global Variables
captured_packets = []
model_trained = False
model = None
rerouting_logs = []
lock = threading.Lock()  # Thread safety lock

# Packet Capture Function
def packet_callback(packet):
    """Captures packets and extracts relevant fields."""
    try:
        if scapy.IP in packet:
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            proto = packet[scapy.IP].proto
            length = len(packet)
            timestamp = time.time()

            with lock:
                captured_packets.append([timestamp, src_ip, dst_ip, proto, length])
                if len(captured_packets) > 1000:
                    captured_packets.pop(0)  # Keep only last 1000 packets

    except Exception as e:
        print(f"Error capturing packet: {e}")

# Start Background Sniffing
def start_sniffing():
    scapy.sniff(prn=packet_callback, store=False)

def run_sniffing_thread():
    thread = threading.Thread(target=start_sniffing, daemon=True)
    thread.start()

# Process Captured Data
def process_data():
    """Prepares captured packets for model training."""
    with lock:
        if not captured_packets:
            return None

        df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])

    try:
        encoder = LabelEncoder()
        df['Source IP'] = encoder.fit_transform(df['Source IP'])
        df['Destination IP'] = encoder.fit_transform(df['Destination IP'])

        scaler = MinMaxScaler()
        df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']] = scaler.fit_transform(
            df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']]
        )

        # Ensure all values are float32
        df = df.astype(np.float32)

        return df

    except Exception as e:
        print(f"Data processing error: {e}")
        return None

# Create Sequences for LSTM Model
def create_sequences(data, seq_length=10):
    sequences, targets = [], []
    for i in range(len(data) - seq_length):
        sequences.append(data.iloc[i:i + seq_length].values)
        targets.append(data.iloc[i + seq_length]['Length'])
    return np.array(sequences, dtype=np.float32), np.array(targets, dtype=np.float32)

# Train LSTM Model
def train_model():
    """Trains the LSTM model if enough data is available."""
    global model, model_trained

    df = process_data()
    if df is None or len(df) < 20:
        return None  # Not enough data to train

    try:
        seq_length = 10
        X, y = create_sequences(df, seq_length)

        # ✅ Fix: Define explicit input shape to avoid warnings
        model = Sequential([
            Input(shape=(seq_length, X.shape[2])),  
            LSTM(50, return_sequences=True),
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

    except Exception as e:
        print(f"Model training error: {e}")
        return None

# Predict Traffic and Allocate Bandwidth
# def suggest_rerouting():
#     """Predicts congestion level and suggests rerouting actions."""
#     global model, rerouting_logs

#     df = process_data()
#     if df is None or not model_trained:
#         return {"error": "Not enough data or model not trained yet."}

#     try:
#         seq_length = 10
#         X, _ = create_sequences(df, seq_length)

#         if len(X) == 0:
#             return {"error": "Not enough sequence data to predict."}

#         predicted_traffic = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))[0][0]

#         # Bandwidth Allocation Logic
#         if predicted_traffic < 0.1:
#             bandwidth_decision = "Allocate 80% bandwidth"
#         elif 0.1 <= predicted_traffic < 0.2:
#             bandwidth_decision = "Allocate 60% bandwidth"
#         elif 0.2 <= predicted_traffic < 0.3:
#             bandwidth_decision = "Allocate 40% bandwidth"
#         else:
#             bandwidth_decision = "Allocate 20% bandwidth (Severe Congestion)"

#         log_entry = {
#             "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
#             "prediction": float(round(predicted_traffic, 4)),
#             "bandwidth_decision": bandwidth_decision,
#             "rerouting": "⚠️ High congestion detected! Rerouting required." if predicted_traffic > 0.3 else "✅ No rerouting required."
#         }

#         with lock:
#             rerouting_logs.append(log_entry)

#         return log_entry

#     except Exception as e:
#         print(f"Prediction error: {e}")
#         return {"error": "Failed to make prediction."}

import os

def suggest_rerouting():
    global model, rerouting_logs

    df = process_data()
    if df is None or not model_trained:
        return {"error": "Not enough data or model not trained yet."}

    try:
        seq_length = 10
        X, _ = create_sequences(df, seq_length)

        if len(X) == 0:
            return {"error": "Not enough sequence data to predict."}

        predicted_traffic = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))[0][0]

        # Bandwidth Allocation and Rerouting Logic
        if predicted_traffic < 0.1:
            bandwidth_decision = "Allocate 80% bandwidth"
            rerouting_command = None  # No change in routing
        elif 0.1 <= predicted_traffic < 0.2:
            bandwidth_decision = "Allocate 60% bandwidth"
            rerouting_command = None
        elif 0.2 <= predicted_traffic < 0.3:
            bandwidth_decision = "Allocate 40% bandwidth"
            rerouting_command = "ovs-ofctl add-flow s1 priority=100,ip,nw_src=10.0.0.1,nw_dst=10.0.0.2,actions=output:2"
        else:
            bandwidth_decision = "Allocate 20% bandwidth (Severe Congestion)"
            rerouting_command = "ovs-ofctl add-flow s1 priority=200,ip,nw_src=10.0.0.1,nw_dst=10.0.0.2,actions=output:3"

        if rerouting_command:
            os.system(rerouting_command)

        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "prediction": float(round(predicted_traffic, 4)),
            "bandwidth_decision": bandwidth_decision,
            "rerouting": "⚠️ High congestion detected! Traffic rerouted." if predicted_traffic > 0.3 else "✅ No rerouting required."
        }

        with lock:
            rerouting_logs.append(log_entry)

        return log_entry

    except Exception as e:
        print(f"Prediction error: {e}")
        return {"error": "Failed to make prediction."}


# Flask Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/start_sniffing')
def start_capture():
    run_sniffing_thread()
    return jsonify({"status": "Monitoring started..."})

@app.route('/train_model')
def train():
    if train_model():
        return jsonify({"status": "Model trained successfully!"})
    return jsonify({"status": "Not enough data to train model."})

@app.route('/get_bandwidth')
def get_bandwidth():
    decision = suggest_rerouting()
    return jsonify(decision)

@app.route('/get_logs')
def get_logs():
    """Returns rerouting logs."""
    with lock:
        return jsonify({"logs": rerouting_logs})

@app.route('/get_packets')
def get_packets():
    """Returns captured packets."""
    with lock:
        return jsonify({"packets": captured_packets})

@app.route('/predict')
def predict():
    """Returns predicted traffic data."""
    result = suggest_rerouting()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    