$(document).on("click", ".langswitcher", function(event) {
    $.cookie('django_language', event.currentTarget.attributes['x-target-lang'].value);
    location.reload(true);
    return false;
});
