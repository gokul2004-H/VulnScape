document.addEventListener("DOMContentLoaded", function () {
    const resultsBody = document.getElementById("results-body");
    const scanResults = JSON.parse(localStorage.getItem("scanResults"));

    if (!scanResults) {
        resultsBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:red;">No results found!</td></tr>`;
        return;
    }

    function getRiskClass(risk) {
        switch (risk) {
            case "High Risk": return "high-risk";
            case "Medium Risk": return "medium-risk";
            case "Low Risk": return "low-risk";
            case "Informational": return "informational";
            default: return "";
        }
    }

    // Prioritize risk order
    const riskOrder = ["High Risk", "Medium Risk", "Low Risk", "Informational"];

    riskOrder.forEach(risk => {
        if (scanResults[risk]) {
            scanResults[risk].forEach(vuln => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td class="${getRiskClass(risk)}">${risk}</td>
                    <td>${vuln.Name}</td>
                    <td>${vuln.Description}</td>
                    <td>${vuln.Solution}</td>
                    <td><a href="${vuln.URL}" target="_blank">${vuln.URL}</a></td>
                `;
                resultsBody.appendChild(row);
            });
        }
    });
});
