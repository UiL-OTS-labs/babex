$(function () {
    $("#id_criterium").change(function () {
        let self = $(this);
        let correct_value_select = $('#id_criterium_correct_value');
        let criterium = self.val();

        // Destroy select2 so we can add items
        correct_value_select.select2("destroy");

        $('.correct-answer-option').each(function () {
            let el = $(this);
            let disabled = el.attr('data-criterium') != criterium;
            el.attr('disabled', disabled);
            console.log(el)
        });

        correct_value_select.val([]);

        // Re-init select2
        correct_value_select.select2();
    }).change();
});