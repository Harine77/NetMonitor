import requests
import time
import random
import threading
import socket
import sys
import argparse

# Default server URL
SERVER_URL = "http://localhost:5000"

# Simulated network data
source_ips = [f"192.168.1.{i}" for i in range(1, 20)]
dest_ips = ["8.8.8.8", "1.1.1.1", "142.250.180.142", "172.217.21.14", "13.107.21.200"]
protocols = [1, 6, 17]  # ICMP, TCP, UDP

# Command-line arguments
parser = argparse.ArgumentParser(description='Simulate network traffic for testing real-time monitoring')
parser.add_argument('--url', default=SERVER_URL, help=f'Server URL (default: {SERVER_URL})')
parser.add_argument('--interval', type=float, default=0.5, help='Interval between packets in seconds (default: 0.5)')
parser.add_argument('--count', type=int, default=0, help='Number of packets to send (0 = unlimited, default: 0)')
parser.add_argument('--random', action='store_true', help='Use random intervals between packets')

# Function to generate a simulated packet
def generate_packet():
    return {
        "timestamp": time.time(),
        "src_ip": random.choice(source_ips),
        "dst_ip": random.choice(dest_ips),
        "proto": random.choice(protocols),
        "length": random.randint(64, 1500)
    }

# Function to send simulated packets to the server
def send_simulated_packets(args):
    print(f"Starting traffic simulation to {args.url}")
    print(f"Press Ctrl+C to stop")
    
    count = 0
    try:
        while args.count == 0 or count < args.count:
            # Generate and send a packet
            packet = generate_packet()
            
            # In a real implementation, we would send this to the server
            # For now, we'll just print it to simulate
            print(f"[{time.strftime('%H:%M:%S')}] Simulated packet: {packet['src_ip']} -> {packet['dst_ip']} ({packet['length']} bytes)")
            
            # Call the start_sniffing endpoint to trigger packet capture
            try:
                response = requests.get(f"{args.url}/start_sniffing")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Server response: {data}")
                else:
                    print(f"Error: Server returned status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to server: {e}")
            
            count += 1
            
            # Random or fixed interval
            if args.random:
                interval = random.uniform(0.1, args.interval * 2)
            else:
                interval = args.interval
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped by user")
    
    print(f"Sent {count} simulated packets")

# Check server status
def check_server_status(url):
    try:
        response = requests.get(f"{url}/server_status")
        if response.status_code == 200:
            print("Server is running!")
            data = response.json()
            print(f"Packet count: {data.get('packet_count', 'unknown')}")
            print(f"Model trained: {data.get('model_trained', 'unknown')}")
            return True
        else:
            print(f"Server returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        return False

# Main function
if __name__ == "__main__":
    args = parser.parse_args()
    
    # Check if server is running
    if check_server_status(args.url):
        print("Starting traffic simulation...")
        send_simulated_packets(args)
    else:
        print("Server not accessible. Make sure the Flask application is running.")
        print(f"Server URL: {args.url}")
        sys.exit(1) 