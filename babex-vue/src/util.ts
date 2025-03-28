import { createApp } from 'vue'
import messages_en from '@/messages.en.json';
import messages_nl from '@/messages.nl.json';
import MessageBox from './components/MessageBox.vue';

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
    const format = '%d-%m-%Y %H:%M';
    const parts = {
        Y: date.getFullYear(),
        m: date.getMonth() + 1,
        d: date.getDate(),
        H: date.getHours(),
        M: date.getMinutes()
    } as Record<string, number>;

    return format.replace(/%(\w)/g, (_, key: string) => {
        let part = parts[key].toString();
        if (part.length < 2) {
            return '0' + part;
        }
        return part;
    });
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

function confirm(message: string) {
    let promise = new Promise((resolve) => {
        let div = document.createElement('div');
        let mb = createApp(MessageBox, {
            message,
            onOk: () => {resolve(true); mb.unmount()},
            onCancel: () => {resolve(false); mb.unmount()}
        });
        let el = mb.mount(div).$el;
        document.body.appendChild(el);
    });

    return promise;
}

export {confirm, formatDate, formatDateISO, formatTime, formatDateTime, _};
