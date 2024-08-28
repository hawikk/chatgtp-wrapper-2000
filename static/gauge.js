function createGauge(element, score) {
    const width = 180;  // Reduced width
    const height = 100; // Reduced height
    const radius = Math.min(width, height) / 2;
    const centerX = width / 2;
    const centerY = height - 36;

    const svg = d3.select(element)
        .append("svg")
        .attr("width", "100%")  // Make SVG responsive
        .attr("height", "100%") // Make SVG responsive
        .attr("viewBox", `-20 -10 ${width + 40} ${height + 10}`)  // Adjusted viewBox to reduce top padding
        .attr("preserveAspectRatio", "xMidYMid meet");

    const scale = d3.scaleLinear()
        .domain([-10, 10])
        .range([-90, 90]);

    const colorScale = d3.scaleLinear()
        .domain([-10, 0, 10])
        .range(["#FF4136", "#0074D9"]); // Red to Blue

    // Create gradient
    const gradient = svg.append("defs")
        .append("linearGradient")
        .attr("id", "gauge-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%");

    gradient.selectAll("stop")
        .data(colorScale.range())
        .enter().append("stop")
        .attr("offset", (d, i) => i * 50 + "%")
        .attr("stop-color", d => d);

    // Draw the gauge background
    const arc = d3.arc()
        .innerRadius(radius - 20)
        .outerRadius(radius)
        .startAngle(Math.PI / 2)
        .endAngle(-Math.PI / 2);

    svg.append("path")
        .attr("d", arc)
        .attr("transform", `translate(${centerX}, ${centerY})`)
        .style("fill", "url(#gauge-gradient)");

    // Add the needle
    const needle = svg.append("line")
        .attr("x1", centerX)
        .attr("y1", centerY)
        .attr("x2", centerX)
        .attr("y2", centerY - radius + 10) // Adjusted needle size
        .attr("stroke", "#333")
        .attr("stroke-width", 3)
        .attr("transform", `rotate(${scale(score)}, ${centerX}, ${centerY})`);

    // Add the score text
    svg.append("text")
        .attr("x", centerX)
        .attr("y", centerY + 20)
        .attr("text-anchor", "middle")
        .style("font-size", "14px") // Adjusted font size
        .style("font-weight", "bold")
        .text(score.toFixed(1));

    // Add labels
    const labels = [
        { text: "Strong Sell", angle: -90 },
        { text: "Sell", angle: -45 },
        { text: "Hold", angle: 0 },
        { text: "Buy", angle: 45 },
        { text: "Strong Buy", angle: 90 }
    ];

    // Adjust label positioning
    svg.selectAll(".label")
        .data(labels)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", d => centerX + (radius + 10) * Math.cos((d.angle - 90) * Math.PI / 180))  // Reduced offset
        .attr("y", d => centerY + (radius + 10) * Math.sin((d.angle - 90) * Math.PI / 180))  // Reduced offset
        .attr("text-anchor", d => d.angle === 0 ? "middle" : (d.angle < 0 ? "end" : "start"))
        .attr("dominant-baseline", "central")
        .style("font-size", "8px")  // Reduced font size
        .text(d => d.text);
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.gauge').forEach(function(element) {
        const score = parseFloat(element.dataset.score);
        createGauge(element, score);
    });
});
