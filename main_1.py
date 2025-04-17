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
import networkx as nx


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

def build_network_graph(df):
    G = nx.Graph()
    link_weights = df.groupby(["Source IP", "Destination IP"])["Length"].mean().reset_index()

    for _, row in link_weights.iterrows():
        G.add_edge(row["Source IP"], row["Destination IP"], weight=row["Length"])

    return G

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
def allocate_bandwidth(predicted_value):
    if predicted_value < 0.1:
        return "Allocate 80% bandwidth"
    elif 0.1 <= predicted_value < 0.2:
        return "Allocate 60% bandwidth"
    elif 0.2 <= predicted_value < 0.3:
        return "Allocate 40% bandwidth"
    else:
        return "Allocate 20% bandwidth (Severe Congestion)"

def suggest_rerouting():
    global model, rerouting_logs

    df = process_data()
    if df is None or not model_trained or len(df) < 20:
        return {"error": "Not enough data or model not trained yet."}

    try:
        seq_length = 10
        X, _ = create_sequences(df, seq_length)

        if len(X) == 0:
            return {"error": "Not enough sequence data to predict."}

        predicted_traffic = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))[0][0]
        bandwidth_decision = allocate_bandwidth(predicted_traffic)

        reroute_msg = "✅ No rerouting required."
        reroute_path = []

        if predicted_traffic > 0.3:
            G = build_network_graph(df)
            source, destination = df.iloc[-1]['Source IP'], df.iloc[-1]['Destination IP']
            try:
                path = nx.shortest_path(G, source, destination, weight='weight')
                reroute_path = path
                reroute_msg = "⚠️ High congestion detected! Rerouting required."
            except nx.NetworkXNoPath:
                reroute_msg = "⚠️ High congestion, but no alternate path found."

        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "prediction": float(predicted_traffic),
            "bandwidth_decision": str(bandwidth_decision),
            "rerouting": str(reroute_msg),
            "reroute": [str(ip) for ip in reroute_path]
        }

        with lock:
            rerouting_logs.append(log_entry)

        return {
            "prediction": float(round(predicted_traffic, 4)),
            "bandwidth_decision": bandwidth_decision,
            "rerouting": reroute_msg,
            "reroute": reroute_path  # This will be used in the frontend for the graph
        }

    except Exception as e:
        print(f"Prediction error: {e}")
        return {"error": "Failed to make prediction."}

@app.route('/')
def open_page():
    return render_template('open.html')

# Route for the Index Page (main dashboard page)
@app.route('/home')
def home():
    return render_template('index.html')

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
# Add to your existing Flask routes
@app.route('/live_data')
def live_data():
    """Endpoint for live visualization data"""
    with lock:
        # Last 20 packets for the chart
        packets = captured_packets[-20:] if len(captured_packets) >= 20 else captured_packets
        timestamps = [p[0] for p in packets]
        lengths = [p[4] for p in packets]
        
        return jsonify({
            "timestamps": timestamps,
            "lengths": lengths,
            "prediction": suggest_rerouting()  # Includes bandwidth decision
        })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    



# import pandas as pd
# import joblib
# import time
# import networkx as nx
# from scapy.all import sniff, IP, TCP

# # Load pre-trained model and scaler
# model = joblib.load("trained_model.pkl")
# scaler = joblib.load("scaler.pkl")

# # Initialize a log list
# logs = []

# # Function to build a network graph
# def build_network_graph(df):
#     G = nx.Graph()
#     link_weights = df.groupby(["Source IP", "Destination IP"])["Length"].mean().reset_index()

#     for _, row in link_weights.iterrows():
#         G.add_edge(row["Source IP"], row["Destination IP"], weight=row["Length"])

#     return G

# # Function to analyze traffic and make decisions
# def analyze_traffic(df):
#     X = df[["Length", "Time", "Source Port", "Destination Port"]]
#     X_scaled = scaler.transform(X)
#     prediction = model.predict(X_scaled)
#     predicted_traffic = prediction.mean()

#     if predicted_traffic > 0.7:
#         bandwidth_decision = "🔴 Reduce bandwidth"
#     elif predicted_traffic < 0.3:
#         bandwidth_decision = "🟢 Increase bandwidth"
#     else:
#         bandwidth_decision = "🟡 Maintain bandwidth"

#     # Rerouting logic
#     if predicted_traffic > 0.3:
#         G = build_network_graph(df)
#         source, destination = df.iloc[-1]['Source IP'], df.iloc[-1]['Destination IP']
#         try:
#             path = nx.shortest_path(G, source, destination, weight='weight')
#             reroute_msg = f"⚠️ High congestion detected! Suggested rerouting path: {path}"
#         except nx.NetworkXNoPath:
#             reroute_msg = "⚠️ High congestion, but no alternate path found."
#     else:
#         reroute_msg = "✅ No rerouting required."

#     # Add log entry
#     log_entry = {
#         "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
#         "prediction": float(round(predicted_traffic, 4)),
#         "bandwidth_decision": bandwidth_decision,
#         "rerouting": reroute_msg
#     }

#     logs.append(log_entry)

#     # Print the most recent log
#     print(f"[{log_entry['timestamp']}] Traffic: {log_entry['prediction']}, "
#           f"Decision: {log_entry['bandwidth_decision']}, Rerouting: {log_entry['rerouting']}")

# # Function to extract features from packets
# def extract_features(packet):
#     if IP in packet and TCP in packet:
#         return {
#             "Source IP": packet[IP].src,
#             "Destination IP": packet[IP].dst,
#             "Source Port": packet[TCP].sport,
#             "Destination Port": packet[TCP].dport,
#             "Length": len(packet),
#             "Time": time.time()
#         }

# # Sniff packets and process them
# def process_packet(packet):
#     features = extract_features(packet)
#     if features:
#         df = pd.DataFrame([features])
#         analyze_traffic(df)

# # Start sniffing
# if __name__ == "__main__":
#     print("🚦 Real-time network traffic monitoring started...\n")
#     sniff(prn=process_packet, store=False)
