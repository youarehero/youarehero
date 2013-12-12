$(document).on("click", ".langswitcher", function(event) {
    $.cookie('django_language', event.currentTarget.attributes['data-target-lang'].value);
    location.reload(true);
    return false;
});
