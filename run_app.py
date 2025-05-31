"""
Network Monitoring Application Startup Script
--------------------------------------------
This script provides an easy way to start the network monitoring application
with administrator privileges (required for packet sniffing).

Usage:
    python run_app.py [options]

Options:
    --simulate    Start with simulated traffic (no real packet capture)
    --debug       Run in debug mode
    --help        Show this help message

Note: On Windows, you may need to run this script with administrator privileges
to allow Scapy to capture packets.
"""

import os
import sys
import subprocess
import argparse
import time
import threading
import webbrowser
import socket
import random

def check_port_available(port):
    """Check if a port is available"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', port))
        available = True
    except socket.error:
        available = False
    s.close()
    return available

def open_browser(url, delay=2):
    """Open the browser after a delay"""
    print(f"Opening browser to {url} in {delay} seconds...")
    time.sleep(delay)
    webbrowser.open(url)

def start_app(simulate=False, debug=False):
    """Start the network monitoring application"""
    if simulate:
        print("Starting with simulated traffic (no real packet capture)")
        
        # Set environment variable for simulation mode
        os.environ['SIMULATE'] = 'true'
        
        # Import the Flask app (will start simulation automatically based on environment variable)
        from main_1 import app
        
        # Open browser automatically
        browser_thread = threading.Thread(
            target=open_browser,
            args=("http://localhost:5000/diagnostics",),
            daemon=True
        )
        browser_thread.start()
        
        # Run the Flask app
        app.run(debug=debug, host="0.0.0.0", port=5000)
    else:
        # Check if running with administrator privileges
        try:
            # Import scapy to test if packet capture will work
            import scapy.all as scapy
            print("Scapy loaded successfully")
        except Exception as e:
            print(f"Warning: Error importing Scapy: {e}")
            print("You may need administrator privileges to capture packets")
        
        # Run the main script directly
        print("Starting network monitoring application with real packet capture...")
        
        # Unset simulation environment variable (in case it was set)
        if 'SIMULATE' in os.environ:
            del os.environ['SIMULATE']
        
        # Open browser automatically
        browser_thread = threading.Thread(
            target=open_browser,
            args=("http://localhost:5000/diagnostics",),
            daemon=True
        )
        browser_thread.start()
        
        # Import and run the app
        from main_1 import app
        app.run(debug=debug, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Monitoring Application Startup")
    parser.add_argument("--simulate", action="store_true", help="Start with simulated traffic")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    if not check_port_available(5000):
        print("Warning: Port 5000 is already in use.")
        print("The application may not start correctly.")
    
    try:
        start_app(simulate=args.simulate, debug=args.debug)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1) 