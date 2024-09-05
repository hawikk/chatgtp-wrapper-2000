$(document).ready(function() {
    var useMarked = typeof marked !== 'undefined';

    $('.card').click(function() {
        var symbol = $(this).data('symbol');
        var newsSummary = $(this).data('news-summary');
        var stockAnalysis = $(this).data('stock-analysis');
        
        // Update stock symbol
        $('#stock-symbol').text(symbol);
        
        // Populate news list
        var $newsList = $('#news-list').empty();
        if (Array.isArray(newsSummary)) {
            newsSummary.forEach(function(news, index) {
                var newsItem = useMarked ? marked.parse(`${index + 1}. ${news}`) : `${index + 1}. ${news}`;
                $newsList.append($('<li>').html(newsItem));
            });
        } else {
            $newsList.append($('<li>').text("No news available"));
        }
        
        // Populate AI analysis
        var analysisContent = useMarked ? marked.parse(stockAnalysis || "No analysis available") : (stockAnalysis || "No analysis available");
        $('#ai-analysis').html(analysisContent);
        
        // Display the lightbox
        $('#lightbox').fadeIn();
    });

    // Close the lightbox when the close button is clicked
    $('.close').click(function() {
        $('#lightbox').fadeOut();
    });

    // Close the lightbox when clicking outside the content area
    $(window).click(function(event) {
        if ($(event.target).is('#lightbox')) {
            $('#lightbox').fadeOut();
        }
    });

    // Gauge creation
    function createGauge(element, score) {
        const width = 180;
        const height = 100;
        const radius = Math.min(width, height) / 2;
        const centerX = width / 2;
        const centerY = height - 36;

        const svg = d3.select(element)
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `-20 -10 ${width + 40} ${height + 10}`)
            .attr("preserveAspectRatio", "xMidYMid meet");

        const scale = d3.scaleLinear()
            .domain([-10, 10])
            .range([-90, 90]);

        const colorScale = d3.scaleLinear()
            .domain([-10, 0, 10])
            .range(["#FF4136", "#0074D9"]);

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

        const arc = d3.arc()
            .innerRadius(radius - 20)
            .outerRadius(radius)
            .startAngle(Math.PI / 2)
            .endAngle(-Math.PI / 2);

        svg.append("path")
            .attr("d", arc)
            .attr("transform", `translate(${centerX}, ${centerY})`)
            .style("fill", "url(#gauge-gradient)");

        const needle = svg.append("line")
            .attr("x1", centerX)
            .attr("y1", centerY)
            .attr("x2", centerX)
            .attr("y2", centerY - radius + 10)
            .attr("stroke", "#333")
            .attr("stroke-width", 3)
            .attr("transform", `rotate(${scale(score)}, ${centerX}, ${centerY})`);

        svg.append("text")
            .attr("x", centerX)
            .attr("y", centerY + 20)
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .style("font-weight", "bold")
            .text(score.toFixed(1));

        const labels = [
            { text: "Strong Sell", angle: -90 },
            { text: "Sell", angle: -45 },
            { text: "Hold", angle: 0 },
            { text: "Buy", angle: 45 },
            { text: "Strong Buy", angle: 90 }
        ];

        svg.selectAll(".label")
            .data(labels)
            .enter()
            .append("text")
            .attr("class", "label")
            .attr("x", d => centerX + (radius + 10) * Math.cos((d.angle - 90) * Math.PI / 180))
            .attr("y", d => centerY + (radius + 10) * Math.sin((d.angle - 90) * Math.PI / 180))
            .attr("text-anchor", d => d.angle === 0 ? "middle" : (d.angle < 0 ? "end" : "start"))
            .attr("dominant-baseline", "central")
            .style("font-size", "8px")
            .text(d => d.text);
    }

    document.querySelectorAll('.gauge').forEach(function(element) {
        const score = parseFloat(element.dataset.score);
        createGauge(element, score);
    });
});
