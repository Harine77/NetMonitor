// Utility script to check if real-time updates are working
// Add this to your HTML file with a script tag and check the console for output

let lastPacketCount = 0;
let lastTimestamp = Date.now();
let updateCounter = 0;

// Function to check if packet data is updating in real-time
function checkPacketUpdates() {
    fetch('/get_packets')
        .then(response => response.json())
        .then(data => {
            const currentCount = data.packets ? data.packets.length : 0;
            const now = Date.now();
            const timeDiff = (now - lastTimestamp) / 1000; // in seconds
            
            console.log(`[${new Date().toLocaleTimeString()}] Packet check #${++updateCounter}`);
            console.log(`Current packet count: ${currentCount}`);
            
            if (currentCount > lastPacketCount) {
                console.log(`%c✅ REAL-TIME WORKING: ${currentCount - lastPacketCount} new packets in ${timeDiff.toFixed(1)}s`, 'color: green; font-weight: bold');
                const newPackets = data.packets.slice(lastPacketCount);
                console.log('Latest packets:', newPackets);
            } else {
                console.log(`%c❌ NO NEW PACKETS in ${timeDiff.toFixed(1)}s`, 'color: red; font-weight: bold');
            }
            
            lastPacketCount = currentCount;
            lastTimestamp = now;
            console.log('---');
        })
        .catch(error => {
            console.error('Error checking packets:', error);
        });
}

// Function to test if we can start packet capture
function testStartCapture() {
    console.log('Testing packet capture start...');
    fetch('/start_sniffing')
        .then(response => response.json())
        .then(data => {
            console.log('Start sniffing response:', data);
        })
        .catch(error => {
            console.error('Error starting packet capture:', error);
        });
}

// Start checking for packet updates
console.log('Starting real-time monitoring check...');
testStartCapture();
setInterval(checkPacketUpdates, 3000); 