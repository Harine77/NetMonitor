from flask import Flask, render_template, jsonify
import scapy.all as scapy
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import networkx as nx
import threading
import time

app = Flask(__name__)

# Global Variables
captured_packets = []
model = None
model_trained = False
encoder = LabelEncoder()
scaler = MinMaxScaler()

# Function to Capture Live Network Packets
def packet_callback(packet):
    global captured_packets

    if scapy.IP in packet:
        src_ip = packet[scapy.IP].src
        dst_ip = packet[scapy.IP].dst
        proto = packet[scapy.IP].proto
        length = len(packet)
        timestamp = time.time()

        captured_packets.append([timestamp, src_ip, dst_ip, proto, length])

        if len(captured_packets) > 1000:  # Keep only recent 1000 packets
            captured_packets.pop(0)

# Background Thread for Packet Sniffing
def start_sniffing():
    print("🔴 Starting Live Network Monitoring...")
    scapy.sniff(prn=packet_callback, store=False, count=50)

def run_sniffer():
    while True:
        start_sniffing()
        time.sleep(5)  # Capture traffic every 5 seconds

# Convert Captured Data to DataFrame
def process_data():
    if not captured_packets:
        return None

    df = pd.DataFrame(captured_packets, columns=['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length'])

    # Encode IP addresses
    df['Source IP'] = encoder.fit_transform(df['Source IP'])
    df['Destination IP'] = encoder.fit_transform(df['Destination IP'])

    # Normalize Data
    df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']] = scaler.fit_transform(df[['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Length']])
    
    return df

# Create Sequences for LSTM
def create_sequences(data, seq_length=10):
    sequences, targets = [], []

    for i in range(len(data) - seq_length):
        sequences.append(data.iloc[i:i + seq_length].values)
        targets.append(data.iloc[i + seq_length]['Length'])

    return np.array(sequences), np.array(targets)

# Train LSTM Model
def train_model():
    global model, model_trained

    df = process_data()
    if df is None or len(df) < 20:
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
    model.fit(X, y, epochs=5, batch_size=16, validation_split=0.2, verbose=1)

    model_trained = True
    print("✅ Model trained successfully.")
    return model

# Allocate Bandwidth Based on Prediction
def allocate_bandwidth(predicted_value):
    if predicted_value < 0.1:
        return "Allocate 80% bandwidth"
    elif 0.1 <= predicted_value < 0.2:
        return "Allocate 60% bandwidth"
    elif 0.2 <= predicted_value < 0.3:
        return "Allocate 40% bandwidth"
    else:
        return "Allocate 20% bandwidth (Severe Congestion)"

# Build Network Graph for Rerouting
def build_network_graph(df):
    G = nx.Graph()
    link_weights = df.groupby(["Source IP", "Destination IP"])["Length"].mean().reset_index()

    for _, row in link_weights.iterrows():
        G.add_edge(row["Source IP"], row["Destination IP"], weight=row["Length"])

    return G

# Suggest Rerouting
def suggest_rerouting():
    df = process_data()
    if df is None or len(df) < 10 or not model_trained:
        return "Not enough data to predict rerouting."

    seq_length = 10
    X, _ = create_sequences(df, seq_length)

    predicted_traffic = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))[0][0]
    bandwidth_decision = allocate_bandwidth(predicted_traffic)

    print(f"🔹 Predicted Traffic: {predicted_traffic:.4f} → {bandwidth_decision}")

    if predicted_traffic > 0.3:
        print("⚠️ High congestion detected! Recommending rerouting.")
        G = build_network_graph(df)

        source, destination = df.iloc[-1]['Source IP'], df.iloc[-1]['Destination IP']
        try:
            path = nx.shortest_path(G, source, destination, weight='weight')
            return {"congestion": predicted_traffic, "bandwidth": bandwidth_decision, "reroute": path}
        except nx.NetworkXNoPath:
            return {"congestion": predicted_traffic, "bandwidth": bandwidth_decision, "reroute": "No alternate path found."}
    else:
        return {"congestion": predicted_traffic, "bandwidth": bandwidth_decision, "reroute": "No rerouting required."}

# API Route to Get Live Traffic Data
@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    return jsonify(suggest_rerouting())

@app.route('/')
def landing():
    return redirect(url_for('open_page'))

# Dashboard Route
@app.route('/')
def index():
    return render_template('index.html')

# Start Background Traffic Monitoring
threading.Thread(target=run_sniffer, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
