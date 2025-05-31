# Network Monitoring System - Simplified Version

This is a simplified version of the network monitoring application that works without TensorFlow. It simulates real-time network traffic and visualization, mimicking the behavior of the full application.

## Getting Started

### Prerequisites

- Python 3.6+
- Flask
- Requests (for testing)

### Installation

1. No special installation is needed. Just make sure you have the required packages:

```bash
pip install flask requests
```

## Running the Application

1. Start the simplified application:

```bash
python simplified_app.py
```

2. Open your browser and navigate to:
   - Main dashboard: http://localhost:5000/home
   - Analytics page: http://localhost:5000/analytics
   - Diagnostics page: http://localhost:5000/diagnostics (recommended for testing)

## Testing Real-Time Functionality

To verify that the real-time updates are working properly:

1. Start the application as described above
2. In a separate terminal, run the test script:

```bash
python test_real_time.py
```

This script will:
- Check if the server is running
- Verify if the packet count increases over time
- Check if the live data endpoint returns updated information
- Confirm if prediction values change dynamically

If all tests pass, your real-time functionality is working correctly!

## How It Works

This simplified version:

1. **Simulates Network Traffic**: Generates random packets in a background thread
2. **Provides Real-Time Updates**: Continuously adds new data every few seconds
3. **Simulates Predictions**: Generates random predictions for bandwidth allocation
4. **Maintains All API Endpoints**: Keeps the same API structure as the full version

## Key Features

- Real-time packet generation
- Live dashboard updates
- Simulated bandwidth predictions
- Dark/light theme switching
- Diagnostic tools

## Troubleshooting

If you encounter issues:

1. **Pages not updating**: Check browser console for errors (F12)
2. **No data showing**: Make sure the application is running and simulation has started
3. **Server errors**: Check terminal output for Python exceptions
4. **API issues**: Use the diagnostics page to manually test each endpoint

## Differences from Full Version

This simplified version:
- Does not require TensorFlow or Scapy
- Uses simulated data instead of real packet capture
- Generates random predictions instead of using ML models
- Has the same frontend functionality and appearance 