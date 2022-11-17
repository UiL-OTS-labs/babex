$(function () {

    // Allows auto opening when an anchor was specified in the url
    if (window.location.hash) {
        $('body').find(window.location.hash).collapse('show');
    }

    $(".hide-participants").click(function () {
        return confirm(gettext('datamanagement:home:warning:hide_participants'));
    });

    $(".delete-invites").click(function () {
        return confirm(gettext('datamanagement:home:warning:delete_invites'));
    });

    $(".delete-comments").click(function () {
        return confirm(gettext('datamanagement:home:warning:delete_comments'));
    });

    $(".delete-participant").click(function () {
        return confirm(gettext('datamanagement:home:warning:delete_participant'));
    });
});