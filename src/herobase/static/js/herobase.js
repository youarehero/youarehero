$(document).ready(function() {
    $(document).on('click', '.box.collapsible .box-title', function(e) {
        var $headline = $(this);
        var $box = $headline.closest('.box');
        var $content = $box.find('.box-content');
        if ($box.hasClass('collapsed')) {
            $box.removeClass('collapsed');
            $content.slideDown();
        } else {
            $box.addClass('collapsed');
            $content.slideUp();
        }
    });
});