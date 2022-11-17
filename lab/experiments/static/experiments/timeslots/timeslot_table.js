/**
 * This file does the following:
 * - Create a custom datatable instance
 * - Adds a custom button to the DT instance that switches between 2 viewing modes
 * - Handles all checkboxes, so that only the last one for every slot is enabled.
 *   In addition, it enables other checkboxes as needed
 * - It makes sure all checkboxes are properly sent and reset on submit
 * - Gives the remove and remove silently buttons for participants their functionality
 *
 * A few notes:
 * A timeslot can have multiple places (for running participants simultaneously).
 * Every place in a timeslot has it's own row. This has a few implications:
 * - We need to make sure that timeslot rows are always together.
 * - Places in a timeslot aren't actually objects; we keep track of the number
 *   of places with a simple integer in the timeslot model. This means we can't
 *   actually delete a specific place. We can only add/subtract to that integer.
 *   As a result, deleting places can only be done 'bottom up', meaning we will
 *   only enable the delete checkbox of the last place.
 *
 * The table has a special button to enable/disable the rowGroup extension.
 * This will group places under a header indicating the time and date of their
 * timeslot.
 *
 */

/**
 * This function unchecks all checkboxes and makes sure only the last one of each checkbox series is enabled.
 */
function reset_disabled()
{
    $('.timeslot_checkbox').each(function () {
        let el = $(this);
        let last = el.attr('data-last');
        let n = el.attr('data-n');

        // If the current checkbox isn't the last one, disable it
        if(n !== last) {
            el.prop('disabled', true);
        }
    })
}
$(function () {

    // Create a custom DT instance, and add a custom button for rowgrouping
    // This grouping uses the rowGroup plugin for DT
    $('table.dt_custom').DataTable( {
        dom: 'Bfrtip',
        buttons : [
            'copyHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print',
            'pageLength',
            // This button switches between grouped and ungrouped views
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
            // Sort on date and time by default (in that order)
            [3, 'asc'],
            [4, 'asc']
        ],
        rowGroup: {
            enable: false, // Start disabled, grouping isn't preferable as default
            dataSrc: 1
        },
        columnDefs: [ {
            targets: [ 1 ], // Column 1 is used for grouping, and isn't meant to be displayed
            visible: false
        } ],
        lengthMenu: [
            [10, 20, 50, -1],
            ["10", "20", "50", "\u221e"]
        ],
        responsive: true,
        paginationType: "full_numbers",
        pageLength: -1, // Show all slots on the page by default
    } );

    // Enable the master checkbox to disable/enable all other checkboxes
    $('#master_checkbox').change(function () {
        let checked = $(this).is(':checked');
        let checkboxes = $('.timeslot_checkbox');

        checkboxes.prop('checked', checked);
        checkboxes.prop('disabled', checked);

        reset_disabled();
    }).change();

    // This method will enable/disable the checkbox above another checkbox
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

        if(confirm(gettext('timeslot:warning:deleting_timeslots')))
            return true;

        reset_disabled();
        return false;
    });

    $('.icon-delete').click(function () {
        return confirm(gettext('timeslot:warning:deleting_timeslot'));
    });

    $('.icon-silent-remove-participant').click(function () {
        return confirm(gettext('timeslot:warning:confirm_silent_remove_participant'));
    });

    $('.icon-remove-participant').click(function () {
        return confirm(gettext('timeslot:warning:confirm_remove_participant'));
    });

});