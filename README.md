# 🛰️ NetMonitor - Network Monitoring System

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![GitHub stars](https://img.shields.io/github/stars/Harine77/NetMonitor.svg)](https://github.com/Harine77/NetMonitor/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Harine77/NetMonitor.svg)](https://github.com/Harine77/NetMonitor/network)

A lightweight, real-time network monitoring system with live dashboards, diagnostic tools, and simulated bandwidth prediction capabilities. Perfect for educational purposes, development environments, and network monitoring demonstrations without requiring system-level privileges or heavy ML dependencies.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Demo & Documentation](#-demo--documentation)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

## 🎯 Problem Statement

**Bandwidth Management Challenge:** Efficiently allocating and managing bandwidth resources is critical for ensuring optimal network performance and user experience. Traditional bandwidth allocation methods can be inflexible and may not adapt to dynamic traffic demands.

## 🚀 Features

### Core Functionality
- 🔍 **Real-time Packet Simulation** - Simulated network traffic monitoring without requiring root privileges
- 📊 **Live Dashboard** - Interactive web-based dashboard with real-time analytics
- 🤖 **LSTM Prediction Model** - Deep learning for bandwidth forecasting
- 🎯 **Diagnostic Tools** - Built-in network diagnostic utilities and endpoint testing
- 📈 **Performance Analytics** - Traffic analysis, flow monitoring, and performance metrics
- 🌙 **Theme Support** - Dark/Light mode switching for better user experience

## 🛠️ Tech Stack

**Backend**
- Python 3.6+ • Flask • TensorFlow/Keras • NumPy • Pandas

**Machine Learning**
- LSTM Networks • Time Series Analysis • Real-time Prediction

**Frontend**
- HTML5 • CSS3 • JavaScript • Chart.js • Bootstrap

### Development & Deployment
- **Git** - Version control
- **Python Virtual Environment** - Dependency isolation
- **Cross-platform** - Windows, macOS, Linux compatible

### Simulation & Testing
- **Custom Traffic Simulator** - Lightweight packet simulation
- **ML Models** - Simulated machine learning predictions
- **Unit Testing** - Automated testing framework

## 🧠 LSTM Algorithm Implementation

Our system uses **Long Short-Term Memory (LSTM)** neural networks for intelligent bandwidth prediction:

### Architecture
```
Input Layer (Traffic Data) → LSTM Layers (64 units) → Dense Layer → Output (Bandwidth Prediction)
```

### Key Features
- **Time Series Analysis**: Processes historical traffic patterns
- **Real-time Adaptation**: Continuously learns from new data
- **Multi-variate Input**: Considers multiple network parameters
- **Dynamic Scaling**: Adjusts predictions based on current load

### Training Data
- Historical bandwidth usage patterns
- Peak/off-peak traffic analysis  
- Application-specific data consumption
- User behavior patterns

## 📺 Demo & Documentation

### 🎥 Video Demonstration
[![NetMonitor Demo](https://img.shields.io/badge/Watch-Demo%20Video-red.svg?logo=youtube)](https://github.com/user-attachments/assets/6fafb628-96ba-4cc4-8490-a6377d0c9337)  
*Watch our comprehensive demo showcasing all features in action*

[![Watch the Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://github.com/user-attachments/assets/6fafb628-96ba-4cc4-8490-a6377d0c9337)


### 📄 Detailed Report
[![Download Report](https://img.shields.io/badge/Download-PDF%20Report-blue.svg?logo=adobe-acrobat-reader)](https://github.com/user-attachments/files/21333293/NETWORK.PROGRAMMING.LAB.MINI.PROJECT.PPT.pptx)
📄 [NETWORK PROGRAMMING LAB MINI PROJECT PPT.pptx](https://github.com/user-attachments/files/21333293/NETWORK.PROGRAMMING.LAB.MINI.PROJECT.PPT.pptx)


## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Harine77/NetMonitor.git
cd NetMonitor
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv netmonitor_env
netmonitor_env\Scripts\activate

# macOS/Linux
python3 -m venv netmonitor_env
source netmonitor_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Manual Installation:**
```bash
pip install flask requests
```

### 4. Verify Installation
```bash
python --version  # Should show Python 3.6+
pip list          # Should show flask and requests
```

## 🚀 Quick Start

### Method 1: One-Command Launch (Recommended)
```bash
python run_app.py --simulate
```

### Method 2: Manual Setup
```bash
# Terminal 1: Start the main server
python main_1.py

# Terminal 2: Start traffic simulation
python simulate_traffic.py
```

### 3. Access the Application
- **Home Dashboard**: http://localhost:5000/home
- **Analytics Page**: http://localhost:5000/analytics  
- **Diagnostics Tools**: http://localhost:5000/diagnostics
- **API Endpoint**: http://localhost:5000/api/packets

## 💻 Usage

### Dashboard Navigation

#### Home Dashboard (`/home`)
- Real-time packet monitoring
- Live traffic statistics
- System overview widgets
- Quick action buttons

#### Analytics Page (`/analytics`)
- Traffic flow analysis
- Performance metrics visualization
- Historical data trends
- Bandwidth utilization charts

#### Diagnostics Page (`/diagnostics`)
- Network diagnostic tools
- Endpoint connectivity testing
- Model training simulation
- Bandwidth prediction tools

### Key Operations

#### Starting Monitoring
1. Navigate to Diagnostics page
2. Click **"Start Monitoring"**
3. Monitor real-time updates on Dashboard

#### Generating Traffic Data
```bash
# Automatic simulation (recommended)
python run_app.py --simulate

# Manual simulation
python simulate_traffic.py
```

#### Testing Predictions
1. Go to Diagnostics page
2. Click **"Train Model"** (generates sample data)
3. Click **"Predict Bandwidth"**
4. View predictions in Analytics

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive tests
python test_real_time.py
```

**Test Coverage:**
- ✅ Server connectivity
- ✅ API endpoint responses
- ✅ Real-time data updates
- ✅ Prediction functionality
- ✅ Error handling

### Performance Testing
```bash
# Load test with multiple requests
for i in {1..10}; do curl http://localhost:5000/api/packets & done
```

## 🛠️ Troubleshooting

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **No packets showing** | Empty dashboard, no data | Run with `--simulate` flag or check permissions |
| **Page not updating** | Static data, no refresh | Check browser console (F12) for JavaScript errors |
| **Server won't start** | Connection refused | Ensure port 5000 isn't in use: `netstat -an \| grep 5000` |
| **Import errors** | Module not found | Install dependencies: `pip install -r requirements.txt` |
| **Simulation not working** | No traffic data | Run `simulate_traffic.py` in separate terminal |
| **Model training fails** | Prediction errors | Ensure simulation runs for at least 30 seconds |

---

<div align="center">

**⭐ Star this repo if you find it useful!**

[![GitHub stars](https://img.shields.io/github/stars/Harine77/NetMonitor.svg?style=social&label=Star)](https://github.com/Harine77/NetMonitor)
[![GitHub forks](https://img.shields.io/github/forks/Harine77/NetMonitor.svg?style=social&label=Fork)](https://github.com/Harine77/NetMonitor/fork)

Made with ❤️ by Govisha R J [Harine77](https://github.com/Harine77) [Harini-1401](https://github.com/Harini-1401)

</div>

---

*Last updated: July 20, 2025*
