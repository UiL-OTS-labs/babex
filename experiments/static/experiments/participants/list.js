$(function () {
    $('.icon-silent-remove-participant').click(function () {
        return confirm(strings['confirm_silent_remove_participant']);
    });

    $('.icon-remove-participant').click(function () {
        return confirm(strings['confirm_remove_participant']);
    });

});