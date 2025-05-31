import requests
import time
import json

def test_real_time_updates():
    """Test if the real-time functionality is working."""
    print("Testing real-time updates...")
    
    base_url = "http://localhost:5000"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/server_status")
        if response.status_code != 200:
            print("Error: Server not responding correctly")
            return False
        
        print("✅ Server is running")
        status_data = response.json()
        print(f"  - Packet count: {status_data.get('packet_count', 'unknown')}")
        print(f"  - Simulation running: {status_data.get('simulation_running', 'unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the application is running on http://localhost:5000")
        return False
    
    # Check if packet count increases over time
    print("\nChecking if packet count increases (real-time data)...")
    initial_count = get_packet_count(base_url)
    print(f"  - Initial packet count: {initial_count}")
    
    time.sleep(5)  # Wait for 5 seconds
    
    new_count = get_packet_count(base_url)
    print(f"  - New packet count after 5 seconds: {new_count}")
    
    if new_count > initial_count:
        print(f"✅ Packet count increased by {new_count - initial_count} - Real-time data working!")
    else:
        print("❌ Packet count did not increase. Real-time data may not be working")
        return False
    
    # Check live data endpoint
    print("\nChecking if live_data endpoint returns updated data...")
    initial_live_data = get_live_data(base_url)
    
    time.sleep(5)  # Wait for 5 seconds
    
    new_live_data = get_live_data(base_url)
    
    # Check if timestamps are different
    if len(initial_live_data['timestamps']) > 0 and len(new_live_data['timestamps']) > 0:
        if initial_live_data['timestamps'][-1] != new_live_data['timestamps'][-1]:
            print("✅ Live data timestamps are updating - Real-time visualization should work!")
        else:
            print("❌ Live data timestamps are not updating. Real-time visualization may not work")
            return False
    
    # Check if prediction values change
    if initial_live_data['prediction']['prediction'] != new_live_data['prediction']['prediction']:
        print("✅ Prediction values are changing - Real-time predictions working!")
    else:
        print("❌ Prediction values are not changing. Real-time predictions may not work")
        return False
    
    print("\n✅ All tests passed! Real-time functionality is working properly")
    return True

def get_packet_count(base_url):
    """Get the current packet count from the server."""
    try:
        response = requests.get(f"{base_url}/get_packets")
        data = response.json()
        return len(data.get('packets', []))
    except:
        return 0

def get_live_data(base_url):
    """Get the current live data from the server."""
    try:
        response = requests.get(f"{base_url}/live_data")
        return response.json()
    except:
        return {"timestamps": [], "lengths": [], "prediction": {"prediction": 0}}

if __name__ == "__main__":
    print("=" * 60)
    print("  REAL-TIME FUNCTIONALITY TEST FOR NETWORK MONITORING APP")
    print("=" * 60)
    print("This script will test if the real-time updates are working properly.")
    print("Make sure the application is running on http://localhost:5000\n")
    
    test_real_time_updates()
    
    print("\nTest complete. Press Enter to exit...")
    input() 