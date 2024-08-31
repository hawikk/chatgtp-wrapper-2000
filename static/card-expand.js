$(document).ready(function() {
    $('.card').click(function() {
        var symbol = $(this).data('symbol');
        var overview = $('#overview-' + symbol);
        
        // Close other open overviews
        $('.card-overview').not(overview).slideUp();
        
        // Toggle the clicked card's overview
        overview.slideToggle();

        // If the overview is now visible, scroll to it
        if (overview.is(':visible')) {
            $('html, body').animate({
                scrollTop: overview.offset().top - 20
            }, 500);
        }

        // Simple animation to indicate the card was clicked
        $(this).addClass('pulse');
        setTimeout(() => {
            $(this).removeClass('pulse');
        }, 300);

        // Placeholder text update (replace with actual data fetching later)
        overview.find('.news-container p').text('Latest news for ' + symbol + ' would appear here.');
        overview.find('.ai-summary p').text('AI-generated summary for ' + symbol + ' would be displayed in this section.');
    });
});