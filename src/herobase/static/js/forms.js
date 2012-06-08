/**
 * Created with PyCharm.
 * User: raphael
 * Date: 08.06.12
 * Time: 09:51
 * To change this template use File | Settings | File Templates.
 */

var confirm_button = function (elem, text) {
    return $(elem).each(function () {
        $(this).bind('click.confirm', function (e) {
            if(text === undefined) {
                text = "Bist du sicher?";
            }
            var confirmation = confirm(text);
            if (!confirmation) {
                e.preventDefault();
                return false;
            }
        });
    });
};