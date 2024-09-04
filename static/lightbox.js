$(document).ready(function() {
    $('.card').click(function() {
        var symbol = $(this).data('symbol');
        var newsSummary = $(this).data('news-summary');
        var stockAnalysis = $(this).data('stock-analysis');
        
        console.log('Symbol:', symbol);
        console.log('News Summary:', newsSummary);
        console.log('Stock Analysis:', stockAnalysis);
        
        // Populate news list
        var $newsList = $('#news-list').empty();
        if (Array.isArray(newsSummary)) {
            newsSummary.forEach(function(news, index) {
                $newsList.append($('<li>').text(`${index + 1}. ${news}`));
            });
        } else if (typeof newsSummary === 'string') {
            $newsList.append($('<li>').text(newsSummary));
        } else {
            $newsList.append($('<li>').text("No news available"));
        }
        
        // Populate AI analysis
        $('#ai-analysis').text(stockAnalysis || "No analysis available");
        
        // Update the stock symbol in the lightbox
        $('#stock-symbol').text(symbol);
        
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