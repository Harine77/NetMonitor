from flask import Flask, render_template, jsonify, request
import threading
import time
import random
import os
import json
import datetime
import socket
import ipaddress

# Initialize the Flask application
app = Flask(__name__)

# Global Variables
captured_packets = []
model_trained = False
model = None
rerouting_logs = []
security_alerts = []
vulnerability_scans = []  # Store vulnerability scan results
packet_stats = {
    "total": 0,
    "protocols": {},
    "ports": {},
    "top_sources": {},
    "top_destinations": {},
    "traffic_volume": [],
    "bandwidth_usage": []
}
lock = threading.Lock()
simulation_running = False
last_update_time = time.time()

def generate_dummy_packet():
    """Generate a single dummy packet for simulation with realistic network data."""
    timestamp = time.time()
    
    # Common protocols with their numbers
    protocols = {
        1: "ICMP",
        6: "TCP", 
        17: "UDP"
    }
    
    # Define source networks (internal and external)
    internal_networks = ["192.168.1", "10.0.0", "172.16.0"]
    external_domains = ["8.8.8", "142.250.180", "13.107.21", "52.94", "172.217"]
    
    # Generate random source and destination IPs
    src_type = random.choices(["internal", "external"], weights=[0.7, 0.3])[0]
    dst_type = random.choices(["internal", "external"], weights=[0.3, 0.7])[0]
    
    if src_type == "internal":
        net = random.choice(internal_networks)
        src_ip = f"{net}.{random.randint(1, 254)}"
        src_port = random.randint(49152, 65535)  # Ephemeral ports
    else:
        net = random.choice(external_domains)
        src_ip = f"{net}.{random.randint(1, 254)}"
        src_port = random.choice([80, 443, 53, 22, 25])  # Common service ports
    
    if dst_type == "internal":
        net = random.choice(internal_networks)
        dst_ip = f"{net}.{random.randint(1, 254)}"
        dst_port = random.choice([80, 443, 3389, 22, 3306, 8080])  # Common server ports
    else:
        net = random.choice(external_domains)
        dst_ip = f"{net}.{random.randint(1, 254)}"
        dst_port = random.choice([80, 443, 53])  # Common internet service ports
    
    # Select protocol
    proto_num = random.choices([1, 6, 17], weights=[0.1, 0.7, 0.2])[0]
    proto_name = protocols[proto_num]
    
    # Generate packet length based on protocol
    if proto_num == 1:  # ICMP
        length = random.randint(64, 1500)
    elif proto_num == 6:  # TCP
        length = random.randint(64, 1500)
    else:  # UDP
        length = random.randint(64, 512)
    
    # Add flags field for TCP
    flags = None
    if proto_num == 6:
        possible_flags = ["S", "A", "P", "F", "R", "SA", "PA", "FA"]
        flags = random.choice(possible_flags)
    
    # Occasionally generate suspicious packets for security alerts
    is_suspicious = random.random() < 0.05  # 5% chance
    
    # Full packet with additional fields
    packet = [
        timestamp,
        src_ip,
        dst_ip,
        proto_num,
        length,
        src_port,
        dst_port,
        flags,
        is_suspicious
    ]
    
    # Update statistics
    with lock:
        global packet_stats
        packet_stats["total"] += 1
        
        # Update protocol stats
        if proto_name in packet_stats["protocols"]:
            packet_stats["protocols"][proto_name] += 1
        else:
            packet_stats["protocols"][proto_name] = 1
            
        # Update source IP stats
        if src_ip in packet_stats["top_sources"]:
            packet_stats["top_sources"][src_ip] += 1
        else:
            packet_stats["top_sources"][src_ip] = 1
            
        # Update destination IP stats
        if dst_ip in packet_stats["top_destinations"]:
            packet_stats["top_destinations"][dst_ip] += 1
        else:
            packet_stats["top_destinations"][dst_ip] = 1
            
        # Keep only top entries
        packet_stats["top_sources"] = dict(sorted(packet_stats["top_sources"].items(), 
                                            key=lambda x: x[1], reverse=True)[:10])
        packet_stats["top_destinations"] = dict(sorted(packet_stats["top_destinations"].items(), 
                                            key=lambda x: x[1], reverse=True)[:10])
        
        # Update traffic volume (last 20 points)
        current_min = int(timestamp / 60) * 60  # Round to nearest minute
        
        if not packet_stats["traffic_volume"] or packet_stats["traffic_volume"][-1][0] != current_min:
            packet_stats["traffic_volume"].append([current_min, length])
        else:
            packet_stats["traffic_volume"][-1][1] += length
            
        if len(packet_stats["traffic_volume"]) > 20:
            packet_stats["traffic_volume"].pop(0)
        
        # Generate bandwidth in Mbps (simulated)
        bandwidth = length * 8 / 1000000  # Convert bytes to Mbps
        
        # Add bandwidth data point
        if not packet_stats["bandwidth_usage"] or packet_stats["bandwidth_usage"][-1][0] != current_min:
            packet_stats["bandwidth_usage"].append([current_min, bandwidth])
        else:
            packet_stats["bandwidth_usage"][-1][1] += bandwidth
            
        if len(packet_stats["bandwidth_usage"]) > 20:
            packet_stats["bandwidth_usage"].pop(0)
    
    # Generate security alert if suspicious
    if is_suspicious:
        generate_security_alert(packet)
    
    return packet

def generate_security_alert(packet):
    """Generate a security alert based on the packet."""
    timestamp, src_ip, dst_ip, proto, length, src_port, dst_port, flags, _ = packet
    
    alert_types = [
        "Port Scan Detected",
        "Unusual Traffic Pattern",
        "Potential DDoS",
        "Suspicious Connection",
        "Malformed Packet",
        "Excessive Bandwidth Usage",
        "Unauthorized Access Attempt"
    ]
    
    severity_levels = ["Low", "Medium", "High", "Critical"]
    
    alert = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
        "alert_type": random.choice(alert_types),
        "severity": random.choice(severity_levels),
        "source_ip": src_ip,
        "dest_ip": dst_ip,
        "protocol": proto,
        "details": f"Suspicious activity involving {src_ip}:{src_port} -> {dst_ip}:{dst_port}",
        "resolved": False,
        "id": len(security_alerts) + 1
    }
    
    with lock:
        security_alerts.append(alert)
        
        # Keep only the latest 100 alerts
        if len(security_alerts) > 100:
            security_alerts.pop(0)

def simulation_thread_function():
    """Function to run in a thread to simulate packet capture."""
    global simulation_running, last_update_time
    
    simulation_running = True
    print("Starting packet simulation...")
    
    # Generate packets at varying rates to simulate network traffic patterns
    packet_count = 0
    
    while simulation_running:
        # Generate a dummy packet
        packet = generate_dummy_packet()
        
        # Add it to our captured packets with the lock
        with lock:
            captured_packets.append(packet)
            packet_count += 1
            
            # Keep only last 1000 packets
            if len(captured_packets) > 1000:
                captured_packets.pop(0)
        
        # Vary the packet generation rate to simulate real network traffic
        # Busier during "business hours" (if we're in that time frame)
        current_hour = datetime.datetime.now().hour
        is_business_hours = 9 <= current_hour <= 17
        is_night = 0 <= current_hour <= 5
        
        if is_business_hours:
            # More packets during business hours (0.05-0.2 seconds between packets)
            time.sleep(random.uniform(0.05, 0.2))
        elif is_night:
            # Much fewer packets at night (0.5-2 seconds between packets)
            time.sleep(random.uniform(0.5, 2))
        else:
            # Normal traffic (0.1-0.5 seconds between packets)
            time.sleep(random.uniform(0.1, 0.5))
        
        # Every 100 packets, print a status update
        if packet_count % 100 == 0:
            print(f"Generated {packet_count} packets so far")
            last_update_time = time.time()

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

def get_bandwidth_prediction():
    """Generate a simulated bandwidth prediction."""
    # Generate a random prediction between 0 and 0.5
    predicted_traffic = random.uniform(0, 0.5)
    
    # Determine bandwidth allocation
    if predicted_traffic < 0.1:
        bandwidth_decision = "Allocate 80% bandwidth"
    elif 0.1 <= predicted_traffic < 0.2:
        bandwidth_decision = "Allocate 60% bandwidth"
    elif 0.2 <= predicted_traffic < 0.3:
        bandwidth_decision = "Allocate 40% bandwidth"
    else:
        bandwidth_decision = "Allocate 20% bandwidth (Severe Congestion)"
    
    # Determine if rerouting is needed
    reroute_msg = "✅ No rerouting required."
    if predicted_traffic > 0.3:
        reroute_msg = "⚠️ High congestion detected! Rerouting required."
    
    # Create a log entry
    log_entry = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "prediction": float(predicted_traffic),
        "bandwidth_decision": bandwidth_decision,
        "rerouting": reroute_msg,
        "reroute": []  # Empty for simplified version
    }
    
    # Add to logs
    with lock:
        rerouting_logs.append(log_entry)
        # Keep only the latest 100 logs
        if len(rerouting_logs) > 100:
            rerouting_logs.pop(0)
    
    return {
        "prediction": float(round(predicted_traffic, 4)),
        "bandwidth_decision": bandwidth_decision,
        "rerouting": reroute_msg,
        "reroute": []
    }

# Flask Routes
@app.route('/')
def open_page():
    return render_template('open.html')

@app.route('/home')
def home():
    return render_template('index.html')

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

@app.route('/diagnostics')
def diagnostics():
    return render_template('diagnostics.html')

@app.route('/start_sniffing')
def start_capture():
    """Start packet simulation."""
    if not simulation_running:
        start_simulation()
    return jsonify({"status": "Simulation started - packets will be generated automatically"})

@app.route('/stop_sniffing')
def stop_capture():
    """Stop packet simulation."""
    if simulation_running:
        stop_simulation()
    return jsonify({"status": "Simulation stopped"})

@app.route('/train_model')
def train():
    """Simulate model training."""
    # Pretend to train the model
    time.sleep(1)  # Simulate a delay
    return jsonify({"status": "Model training simulated successfully!"})

@app.route('/get_bandwidth')
def get_bandwidth():
    """Get bandwidth allocation prediction."""
    return jsonify(get_bandwidth_prediction())

@app.route('/get_logs')
def get_logs():
    """Return rerouting logs."""
    with lock:
        return jsonify({"logs": rerouting_logs})

@app.route('/get_packets')
def get_packets():
    """Return captured packets."""
    with lock:
        return jsonify({"packets": captured_packets})

@app.route('/predict')
def predict():
    """Return predicted traffic data."""
    return jsonify(get_bandwidth_prediction())

@app.route('/live_data')
def live_data():
    """Endpoint for live visualization data"""
    with lock:
        # Last 20 packets for the chart or fewer if not enough
        packets = captured_packets[-20:] if len(captured_packets) >= 20 else captured_packets
        timestamps = [p[0] for p in packets]
        lengths = [p[4] for p in packets]
        
        return jsonify({
            "timestamps": timestamps,
            "lengths": lengths,
            "prediction": get_bandwidth_prediction()
        })

@app.route('/set_theme_preference', methods=['POST'])
def set_theme_preference():
    """Endpoint for saving user theme preference."""
    preference = request.json.get('darkMode', False)
    return jsonify({"status": "success", "darkMode": preference})

@app.route('/server_status')
def server_status():
    """Return the server status and statistics."""
    with lock:
        return jsonify({
            "status": "running",
            "packet_count": len(captured_packets),
            "last_packet_time": captured_packets[-1][0] if captured_packets else None,
            "model_trained": True,  # Always true in simplified version
            "simulation_running": simulation_running,
            "last_update": time.time() - last_update_time,
            "server_time": time.time()
        })

@app.route('/clear_data')
def clear_data():
    """Clear all captured data."""
    global captured_packets, rerouting_logs, security_alerts, packet_stats
    with lock:
        captured_packets = []
        rerouting_logs = []
        security_alerts = []
        packet_stats = {
            "total": 0,
            "protocols": {},
            "ports": {},
            "top_sources": {},
            "top_destinations": {},
            "traffic_volume": [],
            "bandwidth_usage": []
        }
    return jsonify({"status": "Data cleared"})

@app.route('/analytics_data')
def analytics_data():
    """Return analytics data for the analytics page."""
    with lock:
        # Calculate some additional analytics from captured packets
        packet_count = len(captured_packets)
        
        # Return comprehensive statistics
        return jsonify({
            "packets_total": packet_count,
            "protocols": packet_stats["protocols"],
            "top_sources": packet_stats["top_sources"],
            "top_destinations": packet_stats["top_destinations"],
            "traffic_volume": packet_stats["traffic_volume"],
            "bandwidth_usage": packet_stats["bandwidth_usage"],
            "avg_packet_size": sum(p[4] for p in captured_packets) / max(1, packet_count)
        })

@app.route('/security_data')
def security_data():
    """Return security data for the security page."""
    with lock:
        # Count threats by severity
        severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for alert in security_alerts:
            if alert["severity"] in severity_counts:
                severity_counts[alert["severity"]] += 1
        
        # Count alerts by type
        alert_types = {}
        for alert in security_alerts:
            alert_type = alert["alert_type"]
            if alert_type in alert_types:
                alert_types[alert_type] += 1
            else:
                alert_types[alert_type] = 1
        
        return jsonify({
            "alerts": security_alerts,
            "severity_counts": severity_counts,
            "alert_types": alert_types,
            "total_alerts": len(security_alerts),
            "resolved_alerts": sum(1 for alert in security_alerts if alert["resolved"]),
            "unresolved_alerts": sum(1 for alert in security_alerts if not alert["resolved"])
        })

@app.route('/resolve_alert/<int:alert_id>', methods=['POST'])
def resolve_alert(alert_id):
    """Mark a security alert as resolved."""
    with lock:
        for alert in security_alerts:
            if alert["id"] == alert_id:
                alert["resolved"] = True
                return jsonify({"status": "success", "message": f"Alert {alert_id} marked as resolved"})
        
        return jsonify({"status": "error", "message": f"Alert {alert_id} not found"}), 404

def generate_vulnerability_scan(target="all"):
    """Generate simulated vulnerability scan results."""
    # Simulate delayed scan
    scan_time = time.time()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Generate scan results based on target
    if target == "all":
        devices = ["Servers", "Workstations", "Routers", "Switches"]
        scan_count = random.randint(15, 30)
    elif target == "servers":
        devices = ["Web Server", "Database Server", "File Server", "Mail Server"]
        scan_count = random.randint(5, 10)
    elif target == "workstations":
        devices = ["Desktop PCs", "Laptops", "Thin Clients"]
        scan_count = random.randint(8, 15)
    elif target == "network":
        devices = ["Routers", "Switches", "Firewalls", "Access Points"]
        scan_count = random.randint(3, 8)
    
    # Generate vulnerabilities with different severity levels
    high_count = random.randint(0, 3)
    medium_count = random.randint(2, 8)
    low_count = random.randint(4, 15)
    
    # Generate details for scan
    vulnerabilities = []
    
    # High severity vulnerabilities
    for i in range(high_count):
        vulnerability = {
            "id": f"CVE-{random.randint(2018, 2023)}-{random.randint(1000, 9999)}",
            "name": random.choice([
                "Remote Code Execution", 
                "SQL Injection", 
                "Authentication Bypass",
                "Privilege Escalation",
                "Command Injection"
            ]),
            "severity": "High",
            "device": random.choice(devices),
            "description": "Critical security vulnerability requiring immediate attention."
        }
        vulnerabilities.append(vulnerability)
    
    # Medium severity vulnerabilities
    for i in range(medium_count):
        vulnerability = {
            "id": f"CVE-{random.randint(2018, 2023)}-{random.randint(1000, 9999)}",
            "name": random.choice([
                "Cross-Site Scripting (XSS)", 
                "Directory Traversal", 
                "Information Disclosure",
                "Insecure Configuration",
                "Missing Encryption"
            ]),
            "severity": "Medium",
            "device": random.choice(devices),
            "description": "Moderate security vulnerability that should be addressed soon."
        }
        vulnerabilities.append(vulnerability)
    
    # Low severity vulnerabilities
    for i in range(low_count):
        vulnerability = {
            "id": f"CVE-{random.randint(2018, 2023)}-{random.randint(1000, 9999)}",
            "name": random.choice([
                "Missing HTTP Headers", 
                "Outdated Software", 
                "Weak Password Policy",
                "Insecure Cookie",
                "Missing Security Controls"
            ]),
            "severity": "Low",
            "device": random.choice(devices),
            "description": "Low-risk security issue that should be addressed during regular maintenance."
        }
        vulnerabilities.append(vulnerability)
    
    # Create scan result
    scan_result = {
        "id": len(vulnerability_scans) + 1,
        "timestamp": timestamp,
        "target": target,
        "scan_count": scan_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "status": "completed",
        "vulnerabilities": vulnerabilities
    }
    
    # Add to stored scans with lock for thread safety
    with lock:
        vulnerability_scans.append(scan_result)
        if len(vulnerability_scans) > 10:
            vulnerability_scans.pop(0)  # Keep only the last 10 scans
    
    return scan_result

@app.route('/run_vulnerability_scan', methods=['POST'])
def run_vulnerability_scan():
    """Run a vulnerability scan and return results."""
    try:
        # Get the target from the request or default to "all"
        data = request.json
        target = data.get('target', 'all')
        
        # Start a thread to run the scan to simulate async processing
        def background_scan():
            time.sleep(3)  # Simulate scan taking time
            generate_vulnerability_scan(target)
        
        scan_thread = threading.Thread(target=background_scan)
        scan_thread.daemon = True
        scan_thread.start()
        
        return jsonify({
            "success": True,
            "message": f"Vulnerability scan started for {target}",
            "scan_id": len(vulnerability_scans) + 1
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/get_vulnerability_scans')
def get_vulnerability_scans():
    """Return vulnerability scan results."""
    with lock:
        return jsonify({
            "scans": vulnerability_scans
        })

@app.route('/get_network_map_data')
def get_network_map_data():
    """Return real-time network map data."""
    # Generate random network devices and connections
    nodes = []
    links = []
    
    # Create routers
    router_count = 2
    for i in range(1, router_count + 1):
        nodes.append({
            "id": i,
            "name": f"Router {i}",
            "type": "router",
            "ip": f"192.168.{i}.1",
            "status": random.choice(["online", "warning", "critical", "offline"])
        })
    
    # Create switches
    switch_count = 3
    for i in range(1, switch_count + 1):
        nodes.append({
            "id": router_count + i,
            "name": f"Switch {i}",
            "type": "switch",
            "ip": f"192.168.{i}.254",
            "status": random.choice(["online", "warning", "offline"])
        })
    
    # Create servers and workstations
    device_count = 8
    for i in range(1, device_count + 1):
        device_type = "server" if i <= 4 else "workstation"
        nodes.append({
            "id": router_count + switch_count + i,
            "name": f"{device_type.capitalize()} {i}",
            "type": device_type,
            "ip": f"192.168.{random.randint(1, 3)}.{random.randint(10, 250)}",
            "status": random.choice(["online", "warning", "offline"])
        })
    
    # Create links between devices
    # Router to router
    links.append({
        "source": 1,
        "target": 2,
        "bandwidth": "10 Gbps",
        "status": random.choice(["normal", "congested", "down"])
    })
    
    # Routers to switches
    for i in range(1, router_count + 1):
        for j in range(1, switch_count + 1):
            if random.random() < 0.7:  # 70% chance of connection
                links.append({
                    "source": i,
                    "target": router_count + j,
                    "bandwidth": "1 Gbps",
                    "status": random.choice(["normal", "congested", "down"])
                })
    
    # Switches to devices
    for i in range(1, switch_count + 1):
        for j in range(1, device_count + 1):
            if random.random() < 0.4:  # 40% chance of connection
                links.append({
                    "source": router_count + i,
                    "target": router_count + switch_count + j,
                    "bandwidth": "100 Mbps" if j > 4 else "1 Gbps",
                    "status": random.choice(["normal", "congested", "down"])
                })
    
    return jsonify({
        "nodes": nodes,
        "links": links
    })

if __name__ == "__main__":
    # Generate some initial test data
    print("Generating initial test packets...")
    for i in range(20):
        captured_packets.append(generate_dummy_packet())
    print(f"Added {len(captured_packets)} test packets")
    
    # Start simulation automatically
    start_simulation()
    print("Automatic simulation started")
    
    # Set up a thread to periodically update logs in the background
    def update_logs_periodically():
        while True:
            get_bandwidth_prediction()  # This will add to the logs
            time.sleep(5)  # Update every 5 seconds
    
    log_thread = threading.Thread(target=update_logs_periodically, daemon=True)
    log_thread.start()
    
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000) 