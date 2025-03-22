document.getElementById("scanForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const statusElement = document.getElementById("status");

    statusElement.innerText = "Starting scan...";

    try {
    
        const response = await fetch("http://127.0.0.1:5000/start_scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

        const data = await response.json();
        if (data.error) {
            statusElement.innerText = `Error: ${data.error}`;
            return;
        }

        const scanId = data.scan_id;
        statusElement.innerText = `Scan started: ID ${scanId}`;

        let scanCompleted = false;
        while (!scanCompleted) {
            const statusResponse = await fetch(`http://127.0.0.1:5000/scan_status/${scanId}`);
            if (!statusResponse.ok) throw new Error(`HTTP Error: ${statusResponse.status}`);

            const statusData = await statusResponse.json();
            const progress = statusData.status ?? "0";
            statusElement.innerText = `Scan Progress: ${progress}%`;

            if (progress === "100") scanCompleted = true;
            else await new Promise(resolve => setTimeout(resolve, 5000)); 
        }

   
        const resultsResponse = await fetch("http://127.0.0.1:5000/scan_results");
        if (!resultsResponse.ok) throw new Error(`HTTP Error: ${resultsResponse.status}`);

        const resultsData = await resultsResponse.json();

 
        localStorage.setItem("scanResults", JSON.stringify(resultsData));

     
        console.log("🚀 Results stored in localStorage:", resultsData);

        window.location.href = "results.html";

    } catch (error) {
        statusElement.innerText = `Error: ${error.message}`;
        console.error("Scan error:", error);
    }
});
