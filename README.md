# 🛰️ NetMonitor - Network Monitoring System

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Harine77/NetMonitor.svg)](https://github.com/Harine77/NetMonitor/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Harine77/NetMonitor.svg)](https://github.com/Harine77/NetMonitor/network)

A lightweight, real-time network monitoring system with live dashboards, diagnostic tools, and simulated bandwidth prediction capabilities. Perfect for educational purposes, development environments, and network monitoring demonstrations without requiring system-level privileges or heavy ML dependencies.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Demo & Documentation](#-demo--documentation)
- [Prerequisites](#️-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Core Functionality
- 🔍 **Real-time Packet Simulation** - Simulated network traffic monitoring without requiring root privileges
- 📊 **Live Dashboard** - Interactive web-based dashboard with real-time analytics
- 🤖 **Bandwidth Prediction** - Simulated ML-based bandwidth forecasting (lightweight alternative to TensorFlow)
- 🎯 **Diagnostic Tools** - Built-in network diagnostic utilities and endpoint testing
- 📈 **Performance Analytics** - Traffic analysis, flow monitoring, and performance metrics
- 🌙 **Theme Support** - Dark/Light mode switching for better user experience

### Advanced Features
- ⚡ **Real-time Updates** - Live data streaming with WebSocket-like functionality
- 🔧 **API Integration** - RESTful API for external tool integration
- 📱 **Responsive Design** - Mobile-friendly interface
- 🛡️ **Error Handling** - Robust error management and logging
- 🔄 **Auto-refresh** - Automatic data refresh capabilities

## 🛠️ Tech Stack

### Backend
- **Python 3.6+** - Core programming language
- **Flask 2.0+** - Web framework for API and web interface
- **Requests** - HTTP library for external API calls
- **JSON** - Data interchange format
- **Threading** - Concurrent processing for real-time features

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with Flexbox/Grid
- **JavaScript (ES6+)** - Client-side interactivity
- **Chart.js** - Data visualization and charts
- **Bootstrap** - Responsive design framework
- **Font Awesome** - Icon library

### Development & Deployment
- **Git** - Version control
- **Python Virtual Environment** - Dependency isolation
- **Cross-platform** - Windows, macOS, Linux compatible

### Simulation & Testing
- **Custom Traffic Simulator** - Lightweight packet simulation
- **Mock ML Models** - Simulated machine learning predictions
- **Unit Testing** - Automated testing framework

## 📺 Demo & Documentation

### 🎥 Video Demonstration
[![NetMonitor Demo](https://img.shields.io/badge/Watch-Demo%20Video-red.svg?logo=youtube)](link-to-your-video)

*Watch our comprehensive demo showcasing all features in action*

### 📄 Detailed Report
[![Download Report](https://img.shields.io/badge/Download-PDF%20Report-blue.svg?logo=adobe-acrobat-reader)](link-to-your-pdf)

*Complete technical documentation and analysis report*

## ⚙️ Prerequisites

- **Python 3.6 or higher**
- **pip** (Python package installer)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **4GB RAM** minimum (recommended: 8GB)
- **50MB** free disk space

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python    | 3.6+    | 3.8+        |
| RAM       | 2GB     | 4GB         |
| Storage   | 50MB    | 100MB       |
| Network   | Any     | Broadband   |

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

### Manual Testing Checklist
- [ ] Dashboard loads correctly
- [ ] Real-time updates working
- [ ] All navigation links functional
- [ ] Theme switching works
- [ ] API returns valid JSON
- [ ] Diagnostic tools respond
- [ ] Mobile responsiveness

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

### Common Solutions

#### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux  
lsof -ti:5000 | xargs kill -9
```

#### Permission Issues
```bash
# Ensure proper file permissions
chmod +x run_app.py simulate_traffic.py
```

#### Python Path Issues
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 🔗 API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/api/packets` | Fetch current packet data | JSON array of packets |
| GET | `/api/stats` | Get traffic statistics | JSON stats object |
| POST | `/api/predict` | Request bandwidth prediction | JSON prediction data |
| GET | `/api/health` | Server health check | Status message |

### Example API Calls

#### Fetch Packets
```bash
curl -X GET http://localhost:5000/api/packets
```

**Response:**
```json
[
  {
    "timestamp": "2025-07-20T10:30:45",
    "source": "192.168.1.100",
    "destination": "192.168.1.1",
    "protocol": "TCP",
    "size": 1024,
    "port": 80
  }
]
```

#### Get Statistics
```bash
curl -X GET http://localhost:5000/api/stats
```

**Response:**
```json
{
  "total_packets": 1250,
  "bandwidth_usage": 85.2,
  "active_connections": 42,
  "uptime": "2h 15m"
}
```

## 📁 Project Structure

```
NetMonitor/
├── 📄 README.md                 # Project documentation
├── 📄 requirements.txt          # Python dependencies
├── 📄 LICENSE                   # MIT license
├── 🐍 main_1.py                # Main Flask application
├── 🐍 run_app.py               # Application launcher
├── 🐍 simulate_traffic.py      # Traffic simulation script
├── 🐍 test_real_time.py        # Testing utilities
├── 📁 templates/               # HTML templates
│   ├── 🌐 base.html            # Base template
│   ├── 🏠 home.html            # Home dashboard
│   ├── 📊 analytics.html       # Analytics page
│   └── 🔧 diagnostics.html     # Diagnostic tools
├── 📁 static/                  # Static assets
│   ├── 🎨 css/
│   │   └── style.css           # Custom styles
│   ├── 📱 js/
│   │   └── app.js              # Client-side logic
│   └── 🖼️ images/             # Images and icons
├── 📁 docs/                    # Documentation
│   ├── 📄 API_Documentation.pdf # API reference
│   └── 🎥 Demo_Video.mp4       # Feature demonstration
└── 📁 tests/                   # Test files
    └── 🧪 test_suite.py        # Unit tests
```

## 🔄 Comparison: Simplified vs Full Version

| Feature | Simplified Version | Full Version |
|---------|-------------------|--------------|
| **Packet Capture** | ✅ Simulated traffic | ⚡ Real Scapy integration |
| **ML Predictions** | 🤖 Random simulation | 🧠 TensorFlow models |
| **Dependencies** | 📦 Lightweight (Flask, Requests) | 🏗️ Heavy (TensorFlow, Scapy, etc.) |
| **System Access** | 👤 User-level permissions | 🔐 Admin/root required |
| **Setup Time** | ⚡ < 2 minutes | 🕐 10-15 minutes |
| **Resource Usage** | 💾 ~50MB RAM | 💽 ~500MB+ RAM |
| **Platform Support** | ✅ Windows, macOS, Linux | ⚠️ Limited by dependencies |
| **Learning Curve** | 📈 Beginner-friendly | 📊 Advanced users |

## 🎯 Use Cases

### Educational
- **Network Monitoring Concepts** - Learn monitoring principles without complex setup
- **Web Development** - Practice Flask, JavaScript, and API development
- **System Architecture** - Understand real-time systems design

### Development & Testing
- **Prototype Development** - Test monitoring interfaces rapidly
- **API Testing** - Validate network monitoring API designs
- **UI/UX Design** - Experiment with dashboard layouts

### Demonstration
- **Portfolio Projects** - Showcase full-stack development skills
- **Technical Presentations** - Demonstrate monitoring concepts
- **Proof of Concept** - Validate monitoring system ideas

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup
```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/NetMonitor.git
cd NetMonitor

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push to your fork and create Pull Request
git push origin feature/amazing-feature
```

### Contribution Guidelines
- Follow Python PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure cross-platform compatibility

### Areas for Contribution
- 🐛 Bug fixes and improvements
- ✨ New dashboard features
- 🎨 UI/UX enhancements
- 📚 Documentation updates
- 🧪 Additional test coverage
- 🌐 Internationalization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Harine77

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation details...
```

## 🙏 Acknowledgments

- **Flask Community** - For the excellent web framework
- **Bootstrap Team** - For responsive design components
- **Chart.js** - For beautiful data visualizations
- **Open Source Community** - For inspiration and best practices

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/Harine77/NetMonitor/issues)
- **Email**: [Contact maintainer](mailto:your-email@example.com)
- **Documentation**: [Wiki pages](https://github.com/Harine77/NetMonitor/wiki)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

[![GitHub stars](https://img.shields.io/github/stars/Harine77/NetMonitor.svg?style=social&label=Star)](https://github.com/Harine77/NetMonitor)
[![GitHub forks](https://img.shields.io/github/forks/Harine77/NetMonitor.svg?style=social&label=Fork)](https://github.com/Harine77/NetMonitor/fork)

Made with ❤️ by [Harine77](https://github.com/Harine77)

</div>

---

*Last updated: July 20, 2025*
