async function getStockSummary() {
    const ticker = document.getElementById('ticker').value;
    const summaryDiv = document.getElementById('summary');

    if (!ticker) {
        alert("Please enter a stock ticker.");
        return;
    }

    summaryDiv.innerHTML = "<p class='loading'>Loading...</p>";

    try {
        const response = await fetch(`http://127.0.0.1:5000/get-summary?ticker=${ticker}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        summaryDiv.innerHTML = `<h2>Summary for ${ticker}:</h2><p>${data.summary}</p>`;
    } catch (error) {
        console.error("Fetch error:", error);
        summaryDiv.innerHTML = "<p class='error'>Failed to fetch the summary. Please try again later.</p>";
    }
}
