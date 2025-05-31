// Security page visualizations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme toggle if available
    if (typeof initThemeToggle === 'function') {
        initThemeToggle();
    }

    // Initialize security visualizations
    initSecurityVisualizations();
    
    // Initialize attack trends chart
    initAttackTrendsChart();
    
    // Initialize vulnerability chart
    initVulnerabilityChart();
    
    // Set up vulnerability scan functionality
    setupVulnerabilityScan();
    
    // Start polling for vulnerability scan results
    pollVulnerabilityScans();
});

// Initialize Security Visualizations
function initSecurityVisualizations() {
    // Add security stats counters animation
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(statValue => {
        const targetValue = parseInt(statValue.textContent);
        animateCounter(statValue, 0, targetValue);
    });
}

// Animate counter from start to end value
function animateCounter(element, start, end) {
    let current = start;
    const increment = end / 50; // Divide into 50 steps
    const duration = 1500; // 1.5 seconds
    const stepTime = duration / 50;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        
        // If it's a percentage, add % symbol
        if (element.textContent.includes('%')) {
            element.textContent = Math.round(current) + '%';
        } else {
            element.textContent = Math.round(current);
        }
    }, stepTime);
}

// Initialize Attack Trends Chart
function initAttackTrendsChart() {
    const chartContainer = document.getElementById('attack-trends-chart');
    if (!chartContainer) return;
    
    // If Chart.js is available
    if (typeof Chart !== 'undefined') {
        const ctx = chartContainer.getContext('2d');
        
        // Sample data for the last 7 days
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const data = {
            labels: labels,
            datasets: [
                {
                    label: 'DDoS Attacks',
                    data: [65, 78, 52, 91, 43, 29, 47],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Malware Detections',
                    data: [28, 42, 35, 27, 69, 34, 21],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Auth Failures',
                    data: [31, 52, 48, 36, 25, 19, 33],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }
            ]
        };
        
        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else {
        // Fallback if Chart.js is not available
        chartContainer.innerHTML = '<p>Chart.js not loaded. Attack trends visualization unavailable.</p>';
    }
}

// Initialize Vulnerability Chart
function initVulnerabilityChart() {
    const chartContainer = document.getElementById('vulnerability-chart');
    if (!chartContainer) return;
    
    // If Chart.js is available
    if (typeof Chart !== 'undefined') {
        const ctx = chartContainer.getContext('2d');
        
        // Vulnerability data
        const data = {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [3, 8, 12, 5],
                backgroundColor: [
                    '#ef4444', // Critical - red
                    '#f59e0b', // High - orange
                    '#3b82f6', // Medium - blue
                    '#10b981'  // Low - green
                ],
                borderWidth: 1
            }]
        };
        
        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                let value = context.parsed || 0;
                                let total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                let percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    } else {
        // Fallback if Chart.js is not available
        chartContainer.innerHTML = '<p>Chart.js not loaded. Vulnerability chart unavailable.</p>';
    }
}

// Set up vulnerability scan functionality
function setupVulnerabilityScan() {
    // Add event listener for starting a vulnerability scan
    const startScanBtn = document.getElementById('start-scan-btn');
    if (startScanBtn) {
        startScanBtn.addEventListener('click', startVulnerabilityScan);
    }
    
    // Add event listener for scheduling a vulnerability scan
    const scheduleScanBtn = document.getElementById('schedule-scan-btn');
    if (scheduleScanBtn) {
        scheduleScanBtn.addEventListener('click', function() {
            alert('Scan scheduling feature coming soon!');
        });
    }
    
    // Fetch initial scans
    fetchVulnerabilityScans();
}

// Start a vulnerability scan
function startVulnerabilityScan() {
    const target = document.getElementById('scan-target').value;
    
    // Show scan in progress
    updateScanStatus('Scanning...');
    
    // Call server to initiate vulnerability scan
    fetch('/run_vulnerability_scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ target: target })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI to show scan in progress
            updateScanStatus('Scan in progress...');
            
            // Add a temporary scan result
            const scanResultsList = document.getElementById('scan-results-container');
            const tempScanItem = document.createElement('div');
            tempScanItem.className = 'scan-result-item';
            tempScanItem.innerHTML = `
                <div class="scan-result-header">
                    <span class="scan-date">${new Date().toLocaleString()}</span>
                    <span class="scan-target-type">${target.charAt(0).toUpperCase() + target.slice(1)}</span>
                </div>
                <div class="scan-summary">
                    <span class="scan-progress">Scanning... <div class="scan-spinner"></div></span>
                </div>
            `;
            
            // Add this temporary item at the top
            if (scanResultsList.firstChild) {
                scanResultsList.insertBefore(tempScanItem, scanResultsList.firstChild);
            } else {
                scanResultsList.appendChild(tempScanItem);
            }
        } else {
            alert('Failed to start vulnerability scan: ' + data.error);
            updateScanStatus('Scan failed to start');
        }
    })
    .catch(error => {
        console.error('Error starting vulnerability scan:', error);
        alert('Error starting vulnerability scan. Please try again.');
        updateScanStatus('Error starting scan');
    });
}

// Update the scan status display
function updateScanStatus(statusText) {
    const lastScanTime = document.getElementById('last-scan-time');
    if (lastScanTime) {
        if (statusText === 'Scanning...' || statusText === 'Scan in progress...') {
            lastScanTime.innerHTML = `${statusText} <div class="scan-spinner"></div>`;
        } else {
            lastScanTime.textContent = statusText;
        }
    }
}

// Fetch and display vulnerability scans
function fetchVulnerabilityScans() {
    fetch('/get_vulnerability_scans')
        .then(response => response.json())
        .then(data => {
            displayVulnerabilityScans(data.scans);
            
            // Update the last scan time if there are scans
            if (data.scans && data.scans.length > 0) {
                const lastScan = data.scans[data.scans.length - 1];
                updateScanStatus(lastScan.timestamp);
                
                // Also update the vulnerability chart
                updateVulnerabilityChart(lastScan);
            }
        })
        .catch(error => {
            console.error('Error fetching vulnerability scans:', error);
        });
}

// Display vulnerability scan results
function displayVulnerabilityScans(scans) {
    const scanResultsList = document.getElementById('scan-results-container');
    if (!scanResultsList) return;
    
    // Clear any existing scan results (except those with spinner)
    const existingResults = scanResultsList.querySelectorAll('.scan-result-item:not(:has(.scan-spinner))');
    existingResults.forEach(result => result.remove());
    
    // Don't display anything if no scans
    if (!scans || scans.length === 0) {
        const noScans = document.createElement('div');
        noScans.className = 'scan-result-item';
        noScans.innerHTML = `
            <div class="scan-result-header">
                <span class="scan-date">No scans performed</span>
                <span class="scan-target-type">--</span>
            </div>
            <div class="scan-summary">
                <span>Run a scan to see results</span>
            </div>
        `;
        scanResultsList.appendChild(noScans);
        return;
    }
    
    // Remove any temporary scan item with spinner
    const tempItems = scanResultsList.querySelectorAll('.scan-result-item:has(.scan-spinner)');
    tempItems.forEach(item => item.remove());
    
    // Sort scans by timestamp (newest first)
    scans.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Display each scan
    scans.forEach(scan => {
        const scanItem = document.createElement('div');
        scanItem.className = 'scan-result-item';
        
        // Format target name nicely
        const targetName = scan.target.charAt(0).toUpperCase() + scan.target.slice(1);
        
        scanItem.innerHTML = `
            <div class="scan-result-header">
                <span class="scan-date">${scan.timestamp}</span>
                <span class="scan-target-type">${targetName}</span>
            </div>
            <div class="scan-summary">
                <span class="scan-high">${scan.high_count} High</span>
                <span class="scan-medium">${scan.medium_count} Medium</span>
                <span class="scan-low">${scan.low_count} Low</span>
            </div>
            <div class="scan-actions">
                <button class="view-scan-btn" data-scan-id="${scan.id}">View Details</button>
            </div>
        `;
        
        scanResultsList.appendChild(scanItem);
    });
    
    // Add event listeners to view scan details buttons
    const viewButtons = scanResultsList.querySelectorAll('.view-scan-btn');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const scanId = this.getAttribute('data-scan-id');
            viewScanDetails(scans.find(scan => scan.id == scanId));
        });
    });
}

// View detailed scan results
function viewScanDetails(scan) {
    if (!scan) return;
    
    // Create a modal or dialog to show scan details
    const modal = document.createElement('div');
    modal.className = 'scan-details-modal';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'scan-details-content';
    
    // Sort vulnerabilities by severity (high to low)
    const sortedVulnerabilities = [...scan.vulnerabilities].sort((a, b) => {
        const severityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
        return severityOrder[b.severity] - severityOrder[a.severity];
    });
    
    modalContent.innerHTML = `
        <div class="scan-details-header">
            <h3>Scan Results: ${scan.target.charAt(0).toUpperCase() + scan.target.slice(1)}</h3>
            <span class="scan-details-close">&times;</span>
        </div>
        <div class="scan-details-info">
            <p><strong>Date:</strong> ${scan.timestamp}</p>
            <p><strong>Devices Scanned:</strong> ${scan.scan_count}</p>
            <p><strong>Vulnerabilities Found:</strong> ${scan.high_count + scan.medium_count + scan.low_count}</p>
        </div>
        <div class="scan-details-vulnerabilities">
            <h4>Vulnerabilities</h4>
            <table class="vulnerabilities-table">
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Device</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortedVulnerabilities.map(vuln => `
                        <tr class="severity-${vuln.severity.toLowerCase()}">
                            <td>${vuln.severity}</td>
                            <td>${vuln.id}</td>
                            <td>${vuln.name}</td>
                            <td>${vuln.device}</td>
                            <td>${vuln.description}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Add event listener to close button
    const closeButton = modal.querySelector('.scan-details-close');
    closeButton.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Update vulnerability chart with scan data
function updateVulnerabilityChart(scan) {
    // Find the chart instance
    const chartElement = document.getElementById('vulnerability-chart');
    if (!chartElement) return;
    
    const chartInstance = Chart.getChart(chartElement);
    if (!chartInstance) return;
    
    // Update chart data
    chartInstance.data.datasets[0].data = [
        scan.high_count,
        scan.medium_count,
        scan.low_count
    ];
    
    // Update chart
    chartInstance.update();
}

// Poll for new vulnerability scan results periodically
function pollVulnerabilityScans() {
    // Poll every 5 seconds
    setInterval(fetchVulnerabilityScans, 5000);
}

// Add CSS for the vulnerability scan UI
function addVulnerabilityScanStyles() {
    // Check if styles already exist
    if (document.getElementById('vulnerability-scan-styles')) return;
    
    const styleElement = document.createElement('style');
    styleElement.id = 'vulnerability-scan-styles';
    styleElement.textContent = `
        .scan-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0, 0, 0, 0.1);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            vertical-align: middle;
            margin-left: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .scan-details-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .scan-details-content {
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            width: 80%;
            max-width: 1000px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .scan-details-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .scan-details-close {
            font-size: 24px;
            cursor: pointer;
        }
        
        .vulnerabilities-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .vulnerabilities-table th, .vulnerabilities-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .vulnerabilities-table th {
            background-color: #f8fafc;
        }
        
        .severity-high {
            background-color: rgba(239, 68, 68, 0.1);
        }
        
        .severity-medium {
            background-color: rgba(245, 158, 11, 0.1);
        }
        
        .severity-low {
            background-color: rgba(59, 130, 246, 0.1);
        }
        
        .scan-result-item {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        
        .scan-result-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #64748b;
        }
        
        .scan-summary {
            display: flex;
            gap: 15px;
        }
        
        .scan-high {
            color: #ef4444;
            font-weight: 600;
        }
        
        .scan-medium {
            color: #f59e0b;
            font-weight: 600;
        }
        
        .scan-low {
            color: #3b82f6;
            font-weight: 600;
        }
        
        .scan-actions {
            margin-top: 8px;
            text-align: right;
        }
        
        .view-scan-btn {
            padding: 4px 8px;
            background-color: #f1f5f9;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        .view-scan-btn:hover {
            background-color: #e2e8f0;
        }
    `;
    
    document.head.appendChild(styleElement);
}

// Call this function to add styles
addVulnerabilityScanStyles(); 