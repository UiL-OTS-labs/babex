/**
 * This file handles the 'add existing criterion' form. It will make sure that
 * only criterion answers of the selected criterion will show up in the 'correct
 * value' dropdown.
 */
$(function () {
    $("#id_criterion").change(function () {
        let self = $(this);
        let correct_value_select = $('#id_criterion_correct_value');
        // Get the currently chosen criterion
        let criterion = self.val();

        // Destroy select2 so we can change items
        correct_value_select.select2("destroy");

        // Disable all answer options that don't belong to this criterion
        $('.correct-answer-option').each(function () {
            let el = $(this);
            let disabled = el.attr('data-criterion') != criterion;
            el.attr('disabled', disabled);
        });

        // Blank the 'correct value' box
        correct_value_select.val([]);

        // Re-init select2
        correct_value_select.select2();
    }).change(); // We fire the event immediately in order to make sure it also works on load
});