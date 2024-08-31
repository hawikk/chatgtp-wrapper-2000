$(document).ready(function() {
    $('.card').click(function() {
        var symbol = $(this).data('symbol');
        var overviewContent = $('#overview-' + symbol).html();
        
        // Load the content into the lightbox
        $('#lightbox-overview').html(overviewContent);
        
        // Display the lightbox
        $('#lightbox').fadeIn();

        // Placeholder text update (replace with actual data fetching later)
        $('#lightbox-overview .news-container p').text('Latest news for ' + symbol + ' would appear here.');
        $('#lightbox-overview .ai-summary p').text('AI-generated summary for ' + symbol + ' would be displayed in this section.');
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