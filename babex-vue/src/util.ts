
function formatDate(date: Date): string {
    const options = {
        dateStyle: 'short',
    } as const;
    const formatter = new Intl.DateTimeFormat('nl-NL', options);
    return formatter.format(date);
}

function formatTime(date: Date): string {
    const options = {
        timeStyle: 'short',
    } as const;
    const formatter = new Intl.DateTimeFormat('nl-NL', options);
    return formatter.format(date);
}


function formatDateTime(date: Date): string {
    const options = {
        timeStyle: 'short',
        dateStyle: 'short',
    } as const;
    const formatter = new Intl.DateTimeFormat('nl-NL', options);
    return formatter.format(date);
}

export {formatDate, formatTime, formatDateTime};
