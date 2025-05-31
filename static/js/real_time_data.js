/**
 * Real-time Data Management for Network Monitoring Application
 * 
 * This file contains functions to fetch and update real-time data
 * for the analytics and security pages.
 */

// Global variables to store charts
let trafficVolumeChart;
let bandwidthChart;
let protocolChart;
let sourcesChart;
let destinationsChart;
let securityAlertsChart;
let securitySeverityChart;

// Fetch data from the server and update analytics page
function updateAnalyticsData() {
    fetch('/analytics_data')
        .then(response => response.json())
        .then(data => {
            // Update summary statistics
            document.getElementById('total-packets').textContent = data.packets_total.toLocaleString();
            document.getElementById('avg-packet-size').textContent = Math.round(data.avg_packet_size).toLocaleString() + ' bytes';
            
            // Update traffic volume chart
            if (trafficVolumeChart) {
                const labels = data.traffic_volume.map(item => {
                    const date = new Date(item[0] * 1000);
                    return date.toLocaleTimeString();
                });
                const values = data.traffic_volume.map(item => item[1]);
                
                trafficVolumeChart.data.labels = labels;
                trafficVolumeChart.data.datasets[0].data = values;
                trafficVolumeChart.update();
            }
            
            // Update bandwidth usage chart
            if (bandwidthChart) {
                const labels = data.bandwidth_usage.map(item => {
                    const date = new Date(item[0] * 1000);
                    return date.toLocaleTimeString();
                });
                const values = data.bandwidth_usage.map(item => item[1]);
                
                bandwidthChart.data.labels = labels;
                bandwidthChart.data.datasets[0].data = values;
                bandwidthChart.update();
            }
            
            // Update protocol distribution chart
            if (protocolChart) {
                const protocols = Object.keys(data.protocols);
                const protocolCounts = Object.values(data.protocols);
                
                protocolChart.data.labels = protocols;
                protocolChart.data.datasets[0].data = protocolCounts;
                protocolChart.update();
            }
            
            // Update top sources chart
            if (sourcesChart) {
                const sources = Object.keys(data.top_sources);
                const sourceCounts = Object.values(data.top_sources);
                
                sourcesChart.data.labels = sources;
                sourcesChart.data.datasets[0].data = sourceCounts;
                sourcesChart.update();
            }
            
            // Update top destinations chart
            if (destinationsChart) {
                const destinations = Object.keys(data.top_destinations);
                const destinationCounts = Object.values(data.top_destinations);
                
                destinationsChart.data.labels = destinations;
                destinationsChart.data.datasets[0].data = destinationCounts;
                destinationsChart.update();
            }
        })
        .catch(error => console.error('Error fetching analytics data:', error));
}

// Fetch data from the server and update security page
function updateSecurityData() {
    fetch('/security_data')
        .then(response => response.json())
        .then(data => {
            // Update summary statistics
            document.getElementById('total-alerts').textContent = data.total_alerts.toLocaleString();
            document.getElementById('active-threats').textContent = data.unresolved_alerts.toLocaleString();
            document.getElementById('resolved-threats').textContent = data.resolved_alerts.toLocaleString();
            
            // Update severity distribution chart
            if (securitySeverityChart) {
                const severities = Object.keys(data.severity_counts);
                const severityCounts = Object.values(data.severity_counts);
                
                securitySeverityChart.data.labels = severities;
                securitySeverityChart.data.datasets[0].data = severityCounts;
                securitySeverityChart.update();
            }
            
            // Update alert types chart
            if (securityAlertsChart) {
                const alertTypes = Object.keys(data.alert_types);
                const alertCounts = Object.values(data.alert_types);
                
                securityAlertsChart.data.labels = alertTypes;
                securityAlertsChart.data.datasets[0].data = alertCounts;
                securityAlertsChart.update();
            }
            
            // Update alerts table
            updateAlertsTable(data.alerts);
        })
        .catch(error => console.error('Error fetching security data:', error));
}

// Function to update security alerts table
function updateAlertsTable(alerts) {
    const tableBody = document.getElementById('security-alerts-body');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add new rows for each alert, sorted by timestamp (newest first)
    alerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .forEach(alert => {
        const row = document.createElement('tr');
        
        // Determine severity class for color coding
        let severityClass = '';
        switch(alert.severity) {
            case 'Critical': severityClass = 'severity-critical'; break;
            case 'High': severityClass = 'severity-high'; break;
            case 'Medium': severityClass = 'severity-medium'; break;
            case 'Low': severityClass = 'severity-low'; break;
        }
        
        // Build row HTML
        row.innerHTML = `
            <td>${alert.timestamp}</td>
            <td class="${severityClass}">${alert.severity}</td>
            <td>${alert.alert_type}</td>
            <td>${alert.source_ip}</td>
            <td>${alert.dest_ip}</td>
            <td>${alert.details}</td>
            <td>${alert.resolved ? 
                 '<span class="badge badge-success">Resolved</span>' : 
                 '<button class="btn btn-sm btn-warning resolve-alert" data-id="${alert.id}">Resolve</button>'}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to resolve buttons
    document.querySelectorAll('.resolve-alert').forEach(button => {
        button.addEventListener('click', function() {
            const alertId = this.getAttribute('data-id');
            resolveAlert(alertId);
        });
    });
}

// Function to resolve an alert
function resolveAlert(alertId) {
    fetch(`/resolve_alert/${alertId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Refresh security data after resolving alert
            updateSecurityData();
        } else {
            console.error('Error resolving alert:', data.message);
        }
    })
    .catch(error => console.error('Error resolving alert:', error));
}

// Initialize charts for analytics page
function initializeAnalyticsCharts() {
    // Traffic Volume Chart
    const trafficCtx = document.getElementById('traffic-volume-chart');
    if (trafficCtx) {
        trafficVolumeChart = new Chart(trafficCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Traffic Volume (bytes)',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Bytes'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });
    }
    
    // Bandwidth Usage Chart
    const bandwidthCtx = document.getElementById('bandwidth-chart');
    if (bandwidthCtx) {
        bandwidthChart = new Chart(bandwidthCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Bandwidth (Mbps)',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Mbps'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });
    }
    
    // Protocol Distribution Chart
    const protocolCtx = document.getElementById('protocol-chart');
    if (protocolCtx) {
        protocolChart = new Chart(protocolCtx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(46, 204, 113, 0.8)',
                        'rgba(155, 89, 182, 0.8)',
                        'rgba(52, 73, 94, 0.8)',
                        'rgba(243, 156, 18, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Protocol Distribution'
                    }
                }
            }
        });
    }
    
    // Top Sources Chart
    const sourcesCtx = document.getElementById('sources-chart');
    if (sourcesCtx) {
        sourcesChart = new Chart(sourcesCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Packet Count',
                    data: [],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Source IPs'
                    }
                }
            }
        });
    }
    
    // Top Destinations Chart
    const destCtx = document.getElementById('destinations-chart');
    if (destCtx) {
        destinationsChart = new Chart(destCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Packet Count',
                    data: [],
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Destination IPs'
                    }
                }
            }
        });
    }
}

// Initialize charts for security page
function initializeSecurityCharts() {
    // Security Alerts by Type Chart
    const alertsCtx = document.getElementById('security-alerts-chart');
    if (alertsCtx) {
        securityAlertsChart = new Chart(alertsCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Count',
                    data: [],
                    backgroundColor: 'rgba(231, 76, 60, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Alert Types'
                    }
                }
            }
        });
    }
    
    // Security Alerts by Severity Chart
    const severityCtx = document.getElementById('security-severity-chart');
    if (severityCtx) {
        securitySeverityChart = new Chart(severityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(192, 57, 43, 0.8)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(243, 156, 18, 0.8)',
                        'rgba(39, 174, 96, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Alerts by Severity'
                    }
                }
            }
        });
    }
}

// Initialize real-time updates for analytics page
function initAnalyticsPage() {
    console.log('Initializing Analytics Page');
    initializeAnalyticsCharts();
    updateAnalyticsData();
    
    // Set up interval for real-time updates
    setInterval(updateAnalyticsData, 5000);
}

// Initialize real-time updates for security page
function initSecurityPage() {
    console.log('Initializing Security Page');
    initializeSecurityCharts();
    updateSecurityData();
    
    // Set up interval for real-time updates
    setInterval(updateSecurityData, 5000);
}

// Check which page we're on and initialize accordingly
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    if (path.includes('/analytics')) {
        initAnalyticsPage();
    } else if (path.includes('/security')) {
        initSecurityPage();
    }
});

// Export functions for use in other scripts
window.networkMonitoring = {
    updateAnalyticsData,
    updateSecurityData,
    initAnalyticsPage,
    initSecurityPage
}; 