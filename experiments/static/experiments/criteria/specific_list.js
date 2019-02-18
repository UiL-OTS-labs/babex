$(function () {
    $("#id_criterion").change(function () {
        let self = $(this);
        let correct_value_select = $('#id_criterion_correct_value');
        let criterion = self.val();

        // Destroy select2 so we can add items
        correct_value_select.select2("destroy");

        $('.correct-answer-option').each(function () {
            let el = $(this);
            let disabled = el.attr('data-criterion') != criterion;
            el.attr('disabled', disabled);
        });

        correct_value_select.val([]);

        // Re-init select2
        correct_value_select.select2();
    }).change();
});