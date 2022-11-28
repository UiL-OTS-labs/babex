/***
 * This file sets up the needed JS stuff for the threshold widget.
 * There are 3 inputs:
 * - The real input (hidden field)
 * - The fake input (number field)
 * - The mode selector (select field)
 *
 * The real input always holds the threshold expressed in days, as this is what
 * is used by the system. The fake input displays that value in the format (mode)
 * selected in the mode selector. For example, if the threshold is displayed in
 * weeks and the fake input holds a value of 2, the real input will hold '14' as
 * it's value.
 *
 * This file specifically does the following on startup:
 * - It will pull the value from the real input and convert it to the default
 *   mode. It will then set the value of the fake input to that value.
 * - It will register a change event handler on the fake input which will
 *   convert the new value in the fake input to days and set the real input.
 * - Lastly, a change event handler is registered for the mode selector. This
 *   handler will convert the fake input's value to the new mode.
 *
 * NOTE: Calculate with the value of the real input as much as possible. For
 * example, when changing modes we completely ignore the value of the fake input
 * and override it with a new value calculated from the real input. This makes
 * rounding more consistent.
 */

/**
 * This will calculate the number of days from the fake input value and the mode
 * it's in
 * @param val The current value of the fake input
 * @param mode The mode the value is (days, weeks, in)
 * @returns {int} The number of days
 */
function to_days_from_mode(val, mode) {
    switch (mode) {
        case 'years':
            return Math.round(val * 365);
        case 'months':
            return Math.round(val * 30.417);
        case 'weeks':
            return Math.round(val * 7);
        default:
            return Math.round(val);
    }
}

/**
 * This will calculate the value for the fake input from the given value and mode
 * @param val The number of days
 * @param mode The mode (days, weeks, years) to convert to
 * @returns {string} A string representation of the converted value
 */
function from_days_to_mode(val, mode) {
    switch (mode) {
        case 'years':
            return (val / 365).toFixed(2);
        case 'months':
            return (val / 30.417).toFixed(2);
        case 'weeks':
            return (val / 7).toFixed(2);
        default:
            return val.toString();
    }
}

$(function () {

    let selector = $("input[data-threshold=\"true\"]");

    // Custom event to init the whole system
    selector.on('threshold_init', function () {
        // Get all inputs and vars we need
        let el = $(this);
        let name = el.attr('name');
        // So tempted to call this modeselektor
        let mode_selector = $('select[name="'+name+'_mode"]');
        let fake_input = $('input[name="'+name+'_fake"]');

        // Add the correct value to the fake input
        fake_input.val(from_days_to_mode(el.val(), mode_selector.val()));

        // Register an change event handler that sets the value of the real
        // input when the the fake input's value has changed
        fake_input.change(function () {
            el.val(
                to_days_from_mode(
                    $(this).val(),
                    mode_selector.val()
                )
            );
        });

        // Register a change event handler that updates the value of the fake
        // output when the mode is changed
        mode_selector.change(function () {
            fake_input.val(
                from_days_to_mode(
                    el.val(),
                    $(this).val()
                )
            );
        });

    });

    // Trigger the custom init event
    selector.trigger('threshold_init');

});