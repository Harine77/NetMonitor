# Network Monitoring System

This network monitoring application tracks network traffic in real-time, analyzes patterns using machine learning, and provides visualizations and alerts.

## Real-Time Functionality Troubleshooting

If you're experiencing issues with real-time updates on your dashboards, follow these steps to check and fix the problem:

### Option 1: Using the Diagnostics Page

1. Start the application using the simplified launcher:
   ```
   python run_app.py --simulate
   ```

   The `--simulate` flag will generate simulated network traffic, so you don't need to capture real packets.

2. The diagnostics page should open automatically at http://localhost:5000/diagnostics
   
3. Use the buttons on the diagnostics page to test different aspects of the system:
   - **Start Packet Monitoring**: Initiates packet capture
   - **Get Packets**: Retrieves current packet data
   - **Train Model**: Trains the ML model if enough data is available
   - **Make Prediction**: Tests the prediction functionality

4. The real-time log and packet table will show if data is being updated correctly.

### Option 2: Manual Testing with the Simulation Script

1. First, start the application normally:
   ```
   python main_1.py
   ```

2. In a separate terminal, run the simulation script to generate network traffic:
   ```
   python simulate_traffic.py
   ```

3. Open any of these dashboard URLs to see real-time updates:
   - Main dashboard: http://localhost:5000/home
   - Analytics page: http://localhost:5000/analytics
   - Diagnostics page: http://localhost:5000/diagnostics

4. Watch the dashboards for 30-60 seconds to see if data updates automatically.

## Common Issues and Solutions

### No Real-Time Updates

1. **JavaScript Console Errors**: 
   - Open your browser's developer tools (F12) and check the console for errors
   - Ensure that fetch requests to endpoints like `/get_packets` and `/live_data` are succeeding

2. **Backend Issues**:
   - Make sure the Flask server is running properly
   - Check if Scapy is installed and working correctly
   - Verify you have administrative privileges if using real packet capture

3. **Network Permissions**:
   - Windows and macOS may block packet capturing functionality
   - Try running with administrator privileges

### Troubleshooting Cheatsheet

| Problem | Possible Solution |
|---------|-------------------|
| No packets showing | Run with `--simulate` flag or check network permissions |
| Page not updating | Check browser console for errors or reload the page |
| Server not starting | Check if port 5000 is already in use |
| Model training fails | Generate more data first with simulation script |

## Running with Administrator Privileges

### Windows
```
Right-click on Command Prompt/PowerShell -> Run as Administrator
cd path\to\project
python run_app.py
```

### macOS/Linux
```
sudo python run_app.py
```

## Core Features

- Real-time packet capture and analysis
- Machine learning-based traffic prediction
- Bandwidth allocation recommendations
- Network congestion detection
- Dynamic rerouting suggestions
- Dark/light theme switching 