import messages_en from '@/messages.en.json';
import messages_nl from '@/messages.nl.json';

function formatDate(date: Date): string {
    const options = {
        dateStyle: 'short',
    } as const;
    const formatter = new Intl.DateTimeFormat('nl-NL', options);
    return formatter.format(date);
}

function formatDateISO(date: Date): string {
    return date.toISOString().slice(0, 10);
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


/**
 * Resolves translation messages via messages json.
 * Expects window.currentLanguage to be defined.
 */
function _(str: string): string {
    let messages = window.getLanguage() == 'nl' ? messages_nl: messages_en;
    let m = messages as {[key: string]: string|null};
    return m[str] ?? str;
}

export {formatDate, formatDateISO, formatTime, formatDateTime, _};
