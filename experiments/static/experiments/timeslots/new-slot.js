$(function () {
    $('#id_datetime').datetimepicker({
        format: 'yyyy-mm-dd hh:ii',
        weekStart: 1, // Monday
        startDate: new Date(),
        autoclose: true,
        keyboard: false,
        pickerPosition: 'top-left',
        forceParse: false, // We validate manually, as to provide better feedback to the user
    });

    $("#save-new-slot").click(function () {
        let datetime = $('#id_datetime');

        try {
            let dt = datetime.val().split(' ');

            // If we could not split into 2 separate values, something is messed up
            if(dt.length !== 2)
            {
                alert(strings['invalid_datetime']);
                return false
            }

            let date = dt[0];
            let time = dt[1];

            if (!validate_date(date))
            {
                alert(strings['invalid_date']);
                return false;
            }

            if (!validate_time(time))
            {
                alert(strings['invalid_time']);
                return false;
            }

            return true;

        } catch (e) {
            alert(strings['validation_error']);
        }


        return false;
    });
});

const this_year = new Date().getFullYear();

function validate_date(date) {
    /**
     * Validates a date in yyyy-mm-dd format
     */

    if(!/^\d{4}-\d{1,2}-\d{1,2}$/.test(date))
        return false;

    let parts = date.split('-');
    let year = parseInt(parts[0], 10);
    let month = parseInt(parts[1], 10);
    let day = parseInt(parts[2],10);

    if(year < this_year || year > 3000 || month === 0 || month > 12)
        return false;

    let monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // Adjust for leap years
    if(year % 400 === 0 || (year % 100 !== 0 && year % 4 === 0))
        monthLength[1] = 29;

    return day > 0 && day <= monthLength[month - 1];
}

function validate_time(time) {
    /**
     * Validates a time in hh:mm format, no seconds allowed!
     */
    if(!/^\d{1,2}:\d{2}$/.test(time))
        return false;

    let parts = time.split(':');
    let hours = parseInt(parts[0], 10);
    let minutes = parseInt(parts[1], 10);

    return !(hours < 0 || hours > 24 || minutes < 0 || minutes > 59);
}