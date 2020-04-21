/** This file housed a custom datatable config and also handles the 'check all' checkbox. */
$(function () {
    $('.dt_custom').DataTable({
        dom: 'Bfrtip',
        buttons : [
            'copyHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print',
            'pageLength'
        ],
        order: [[3, 'asc'], [0, 'asc']],
        lengthMenu: [
            [10, 25, 50, 100, -1],
            ["10", "25", "50", "100", "\u221e"]
        ],
        responsive: true,
        paginationType: "full_numbers",
        columnDefs: [ {
            targets: 4,
            orderable: false
        }
        ]
    });

    $('#master_checkbox').click(function () {
        let checked = $(this).is(':checked');
        let checkboxes = $('.invite-checkbox');

        checkboxes.prop('checked', checked);
    });
});