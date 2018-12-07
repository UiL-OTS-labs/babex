function reset_disabled()
{
    $('.timeslot_checkbox').each(function () {
        let el = $(this);
        let last = el.attr('data-last');
        let n = el.attr('data-n');

        if(n !== last) {
            el.prop('disabled', true);
        }
    })
}
$(function () {

    $('table.dt_custom').DataTable( {
        dom: 'Bfrtip',
        buttons : [
            'copyHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print',
            'pageLength'
        ],
        order: [
            [2, 'asc'],
            [3, 'asc']
        ],
        lengthMenu: [
            [10, 20, 50, -1],
            ["10", "20", "50", "\u221e"]
        ],
        responsive: true,
        paginationType: "full_numbers",
        pageLength: -1,
    } );


    $('#master_checkbox').change(function () {
        let checked = $(this).is(':checked');
        let checkboxes = $('.timeslot_checkbox');

        checkboxes.prop('checked', checked);
        checkboxes.prop('disabled', checked);

        reset_disabled();
    }).change();

    $('.timeslot_checkbox').change(function () {
        let el = $(this);
        let checked = el.is(':checked');
        let timeslot = el.attr('data-timeslot');
        let n = el.attr('data-n');

        if(n > 0)
        {
            $('#' + timeslot + '-' + (n-1)).prop('disabled', !checked)
        }

    }).change();

    $('#delete-all-selected').click(function () {
        let checkboxes = $('.timeslot_checkbox');

        checkboxes.prop('disabled', false);
    });
});