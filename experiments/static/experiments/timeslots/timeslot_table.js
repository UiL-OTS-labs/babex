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
            'pageLength',
            {
                text: 'Group rows by slot',
                action: function ( e, dt, node, config ) {
                    if (config.state === 'grouped')
                    {
                        config.state = 'ungrouped';
                        dt.rowGroup().disable();
                        this.text('Group rows by slot');
                        dt.columns( [2, 3, 4] ).visible( true );
                    }
                    else if (config.state === 'ungrouped')
                    {
                        config.state = 'grouped';
                        dt.rowGroup().enable();
                        this.text('Ungroup rows');
                        dt.columns( [2, 3, 4] ).visible( false );
                    }
                    dt.draw()
                },
                // rowGroup _should_ have a enabled() method, but it doesn't
                // So we keep track of the state ourselves
                state: 'ungrouped'
            },
        ],
        order: [
            [3, 'asc'],
            [4, 'asc']
        ],
        rowGroup: {
            enable: false,
            dataSrc: 1
        },
        columnDefs: [ {
            targets: [ 1 ],
            visible: false
        } ],
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

        if(confirm(strings['confirm_multi_delete']))
            return true;

        reset_disabled();
        return false;
    });

    $('.icon-delete').click(function () {
        return confirm(strings['confirm_delete']);
    });

    $('.icon-silent-remove-participant').click(function () {
        return confirm(strings['confirm_silent_remove_participant']);
    });

    $('.icon-remove-participant').click(function () {
        return confirm(strings['confirm_remove_participant']);
    });

});