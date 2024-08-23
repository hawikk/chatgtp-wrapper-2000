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

        // Replace newlines with <br> tags and render markdown
        const formattedSummary = data.summary
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Replace **bold** with <strong>bold</strong>
            .replace(/\*(.*?)\*/g, '<em>$1</em>');  // Replace *italic* with <em>italic</em>

        summaryDiv.innerHTML = `<h2>Summary for ${ticker}:</h2><p>${formattedSummary}</p>`;
    } catch (error) {
        console.error("Fetch error:", error);
        summaryDiv.innerHTML = "<p class='error'>Failed to fetch the summary. Please try again later.</p>";
    }
}