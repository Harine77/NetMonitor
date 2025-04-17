// Start Packet Sniffing
function startSniffing() {
    fetch('/start_sniffing')
        .then(response => response.json())
        .then(data => alert(data.status || "Sniffing started successfully!"))
        .catch(error => {
            console.error('Error starting sniffing:', error);
            alert("Error starting packet sniffing.");
        });
}

// Fetch and Display Packets in Real-Time
let lastPacketTimestamp = 0;  // To track new packets only

function fetchPackets() {
    fetch('/get_packets')
        .then(response => response.json())
        .then(data => {
            let tableBody = document.getElementById("packet-data");

            if (!data.packets || data.packets.length === 0) {
                tableBody.innerHTML = "<tr><td colspan='5'>No packets captured yet.</td></tr>";
                return;
            }

            let newPackets = data.packets.filter(packet => packet[0] > lastPacketTimestamp);
            if (newPackets.length === 0) return; // No new packets to update

            newPackets.forEach(packet => {
                let formattedTimestamp = new Date(packet[0] * 1000).toLocaleTimeString(); // Convert UNIX timestamp
                let row = `<tr>
                    <td>${formattedTimestamp}</td>
                    <td>${packet[1] || "N/A"}</td>
                    <td>${packet[2] || "N/A"}</td>
                    <td>${packet[3] || "N/A"}</td>
                    <td>${packet[4] || "N/A"}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });

            lastPacketTimestamp = newPackets[newPackets.length - 1][0]; // Update last timestamp

            // Auto-scroll to the latest packet
            let packetContainer = document.getElementById("packet-container");
            packetContainer.scrollTop = packetContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error fetching packets:', error);    
            document.getElementById("packet-data").innerHTML =
                "<tr><td colspan='5' style='color: red;'>Error retrieving packet data.</td></tr>";
        });
}

// Train Model
function trainModel() {
    fetch('/train_model')
        .then(response => response.json())
        .then(data => alert(data.status || "Model training completed successfully."))
        .catch(error => {
            console.error('Error training model:', error);
            alert("Error occurred while training the model.");
        });
}

// Predict Traffic and Display Results
function fetchPackets(){
    fetch('/get_packets')
.then(response => response.json())
.then(data => {
    console.log("Received packets:", data);  // 🔍 Debugging log

    let tableBody = document.getElementById("packet-data");
    tableBody.innerHTML = ""; // Clear old rows before adding new ones

    if (!data.packets || data.packets.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='5'>No packets captured yet.</td></tr>";
        return;
    }

    let newPackets = data.packets; // Removed filtering for now

    newPackets.forEach(packet => {
        console.log("Adding row:", packet);  // 🔍 Check each packet
        let formattedTimestamp = new Date(packet[0] * 1000).toLocaleTimeString(); // Convert UNIX timestamp
        let row = `<tr>
            <td>${formattedTimestamp}</td>
            <td>${packet[1] || "N/A"}</td>
            <td>${packet[2] || "N/A"}</td>
            <td>${packet[3] || "N/A"}</td>
            <td>${packet[4] || "N/A"}</td>
        </tr>`;
        tableBody.innerHTML += row;
    });
})
.catch(error => console.error('Error fetching packets:', error));

}
setInterval(fetchPackets, 5000);
fetchPackets();



// Fetch packet data every 3 seconds for better real-time updates
setInterval(fetchPackets, 3000);
