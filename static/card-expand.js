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
});