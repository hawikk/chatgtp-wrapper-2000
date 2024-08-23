document.getElementById('stock-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const stockSymbol = document.getElementById('stock-symbol').value;
    const summaryOutput = document.getElementById('summary-output');

    summaryOutput.innerHTML = 'Loading...';

    try {
        const response = await fetch('/get-summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol: stockSymbol })
        });

        if (response.ok) {
            const data = await response.json();
            summaryOutput.innerHTML = `<p>${data.summary}</p>`;
        } else {
            summaryOutput.innerHTML = `<p>Error: ${response.statusText}</p>`;
        }
    } async function getStockSummary() {
        const ticker = document.getElementById('ticker').value;
        if (!ticker) {
            alert("Please enter a stock ticker.");
            return;
        }
    
        const summaryDiv = document.getElementById('summary');
        summaryDiv.innerHTML = "Loading...";
    
        try {
            const response = await fetch(`http://127.0.0.1:5000/get-summary?ticker=${ticker}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            summaryDiv.innerHTML = `<h2>Summary for ${ticker}:</h2><p>${data.summary}</p>`;
        } catch (error) {
            console.error("Fetch error:", error);
            summaryDiv.innerHTML = `<p>Failed to fetch the summary. Please try again later.</p>`;
        }
    }
    
    }
});
