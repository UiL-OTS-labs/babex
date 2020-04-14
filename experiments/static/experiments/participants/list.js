/**
 * This file creates a custom datatable instance, enables the search per-column
 * search functionality and handles the remove-participants buttons.
 */
$(function () {
    let oTable = $('.dt_custom').DataTable({
        dom: 'Bfrtip',
        buttons: [
            'copyHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print',
            'pageLength'
        ],
        order: [[0, 'asc'], [2, 'asc']],
        lengthMenu: [
            [10, 20, 50, -1],
            ["10", "20", "50", "\u221e"]
        ],
        responsive: true,
        pageLength: -1,
        paginationType: "full_numbers",
    });

    // This event handler will initiate a search in the column of the searchbox
    $("tfoot input").keyup(function () {
        // Get the index of this column by making a list of all columns, and
        // looking at what index this column has in the list
        let columnIndex = $("tfoot th").index($(this).parent());

        // Select the column in DT, run a search and do a draw to display the results
        oTable.column(columnIndex).search(this.value).draw();
    });

    // Handles the delete silently button
    $('.icon-silent-remove-participant').click(function () {
        return confirm(strings['confirm_silent_remove_participant']);
    });

    // Handles the regular delete button
    $('.icon-remove-participant').click(function () {
        return confirm(strings['confirm_remove_participant']);
    });

});