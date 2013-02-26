$(document).ready(function() {
    $(document).on('click', '.box.collapsible > .box-title', function(e) {
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

    $('[data-toggle=tooltip]').tooltip();

    $("#hero-cancel").submit(function (e) {
         var confirmed = confirm("Wollen sie wirklich ihre Teilnahme an der Quest zurückziehen?");
        if(!confirmed) {
            e.preventDefault();
        }
    });

    $("#owner-cancel").submit(function (e) {
        var confirmed = confirm("Wollen sie diese Quest wirklich löschen?");
        if(!confirmed) {
            e.preventDefault();
        }
    });
});
