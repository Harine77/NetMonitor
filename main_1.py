from flask import Flask, render_template, jsonify, request
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
import random
import os

# Initialize the Flask application
app = Flask(__name__)

# Global Variables - these need to be global so the simulation thread can access them
global captured_packets, model_trained, model, rerouting_logs, lock
captured_packets = []
model_trained = False
model = None
rerouting_logs = []
lock = threading.Lock()  # Thread safety lock
simulation_running = False  # Track if simulation is running

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
    """Starts packet sniffing with a limit to avoid blocking indefinitely."""
    try:
        # Use a count parameter to avoid blocking indefinitely
        scapy.sniff(prn=packet_callback, store=False, count=100, timeout=10)
        print("Finished capturing packets or timed out")
    except Exception as e:
        print(f"Error in packet sniffing: {e}")

def run_sniffing_thread():
    """Start sniffing in a background thread."""
    thread = threading.Thread(target=start_sniffing, daemon=True)
    thread.start()
    return "Sniffing thread started"

# Process Captured Data
def process_data():
    """Prepares captured packets for model training."""
    with lock:
        if not captured_packets or len(captured_packets) < 10:
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
    """Builds a network graph based on packet data."""
    G = nx.Graph()
    link_weights = df.groupby(["Source IP", "Destination IP"])["Length"].mean().reset_index()

    for _, row in link_weights.iterrows():
        G.add_edge(row["Source IP"], row["Destination IP"], weight=row["Length"])

    return G

# Create Sequences for LSTM Model
def create_sequences(data, seq_length=10):
    """Creates sequence data for the LSTM model."""
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

        if len(X) == 0 or len(y) == 0:
            return None  # Not enough sequence data
            
        # Define explicit input shape to avoid warnings
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
    """Determine bandwidth allocation based on prediction."""
    if predicted_value < 0.1:
        return "Allocate 80% bandwidth"
    elif 0.1 <= predicted_value < 0.2:
        return "Allocate 60% bandwidth"
    elif 0.2 <= predicted_value < 0.3:
        return "Allocate 40% bandwidth"
    else:
        return "Allocate 20% bandwidth (Severe Congestion)"

def suggest_rerouting():
    """Predicts congestion and suggests rerouting."""
    global model, rerouting_logs

    # If no model is trained, return a default prediction for testing
    if not model_trained:
        # Generate a random prediction between 0 and 0.5
        predicted_traffic = random.uniform(0, 0.5)
        bandwidth_decision = allocate_bandwidth(predicted_traffic)
        
        reroute_msg = "✅ No rerouting required."
        if predicted_traffic > 0.3:
            reroute_msg = "⚠️ High congestion detected! Rerouting required."
        
        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "prediction": float(predicted_traffic),
            "bandwidth_decision": bandwidth_decision,
            "rerouting": reroute_msg,
            "reroute": []
        }
        
        with lock:
            rerouting_logs.append(log_entry)
            
        return {
            "prediction": float(round(predicted_traffic, 4)),
            "bandwidth_decision": bandwidth_decision,
            "rerouting": reroute_msg,
            "reroute": []
        }

    # Try with real model prediction
    df = process_data()
    if df is None or len(df) < 20:
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
            "reroute": reroute_path
        }

    except Exception as e:
        print(f"Prediction error: {e}")
        return {"error": "Failed to make prediction."}

# Simulation functions for testing
def generate_dummy_packet():
    """Generate a single dummy packet for simulation."""
    timestamp = time.time()
    src_ip = f"192.168.1.{random.randint(1, 20)}"
    dst_ip = f"192.168.1.{random.randint(21, 40)}"
    proto = random.choice([6, 17])  # TCP or UDP
    length = random.randint(64, 1500)
    
    return [timestamp, src_ip, dst_ip, proto, length]

def simulation_thread_function():
    """Function to run in a thread to simulate packet capture."""
    global simulation_running
    
    simulation_running = True
    print("Starting packet simulation...")
    
    while simulation_running:
        # Generate a dummy packet
        packet = generate_dummy_packet()
        
        # Add it to our captured packets with the lock
        with lock:
            captured_packets.append(packet)
            if len(captured_packets) > 1000:
                captured_packets.pop(0)
                
        # Sleep for a random interval (0.2 to 2 seconds)
        time.sleep(random.uniform(0.2, 2))

def start_simulation():
    """Start the simulation thread."""
    simulation_thread = threading.Thread(target=simulation_thread_function, daemon=True)
    simulation_thread.start()
    print("Simulation thread started")
    return simulation_thread

def stop_simulation():
    """Stop the simulation thread."""
    global simulation_running
    simulation_running = False
    print("Stopping simulation thread")

# Flask Routes
@app.route('/')
def open_page():
    return render_template('open.html')

# Route for the Index Page (main dashboard page)
@app.route('/home')
def home():
    return render_template('index.html')

# Additional routes for sidebar navigation
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/network_map')
def network_map():
    return render_template('network_map.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

# Route for diagnostics page
@app.route('/diagnostics')
def diagnostics():
    return render_template('diagnostics.html')

@app.route('/start_sniffing')
def start_capture():
    """Endpoint to start packet capture (or simulation in testing mode)."""
    # For testing, we'll use simulation instead of real packet capture
    if os.environ.get('SIMULATE', 'false').lower() == 'true':
        # If simulation is enabled through environment variable
        if not simulation_running:
            start_simulation()
        return jsonify({"status": "Simulation started - packets will be generated automatically"})
    else:
        # Real packet capture
        status = run_sniffing_thread()
        return jsonify({"status": status})

@app.route('/start_simulation')
def start_sim_route():
    """Explicit endpoint to start simulation."""
    if not simulation_running:
        start_simulation()
    return jsonify({"status": "Simulation started"})

@app.route('/stop_simulation')
def stop_sim_route():
    """Endpoint to stop simulation."""
    if simulation_running:
        stop_simulation()
    return jsonify({"status": "Simulation stopped"})

@app.route('/train_model')
def train():
    """Endpoint to train the model."""
    result = train_model()
    if result is not None:
        return jsonify({"status": "Model trained successfully!"})
    return jsonify({"status": "Not enough data to train model."})

@app.route('/get_bandwidth')
def get_bandwidth():
    """Endpoint to get bandwidth allocation."""
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

@app.route('/set_theme_preference', methods=['POST'])
def set_theme_preference():
    """Endpoint for saving user theme preference on the server side (if needed)"""
    preference = request.json.get('darkMode', False)
    # Here you could save the preference to a database if needed
    return jsonify({"status": "success", "darkMode": preference})

@app.route('/server_status')
def server_status():
    """Returns the server status and statistics"""
    with lock:
        return jsonify({
            "status": "running",
            "packet_count": len(captured_packets),
            "last_packet_time": captured_packets[-1][0] if captured_packets else None,
            "model_trained": model_trained,
            "simulation_running": simulation_running,
            "server_time": time.time()
        })

@app.route('/clear_data')
def clear_data():
    """Clear all captured data for testing purposes."""
    global captured_packets, rerouting_logs
    with lock:
        captured_packets = []
        rerouting_logs = []
    return jsonify({"status": "Data cleared"})

if __name__ == "__main__":
    # Generate some initial test packets
    print("Generating initial test packets...")
    for i in range(20):
        captured_packets.append(generate_dummy_packet())
    print(f"Added {len(captured_packets)} test packets")
    
    # Set environment variable for simulation mode if needed
    # os.environ['SIMULATE'] = 'true'
    
    # Start simulation automatically if simulation mode is enabled
    if os.environ.get('SIMULATE', 'false').lower() == 'true':
        start_simulation()
        print("Automatic simulation started")
    
    # Run the Flask application
    app.run(debug=True, host="0.0.0.0")
