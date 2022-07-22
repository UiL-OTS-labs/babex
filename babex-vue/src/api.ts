import {urls} from './urls';
import type {Appointment, Closing, Location} from './types';

function getCookie(name: string): string | null {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class ApiClient {
    csrfToken: string;

    constructor() {
        this.csrfToken = getCookie('csrftoken') ?? '';
    }

    headers() {
        return {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
        };
    }

    async get<T>(url: string): Promise<T> {
        const result = await fetch(url, {
            method: 'GET',
            headers: this.headers()
        });

        return await result.json();
    }

    async post<T>(url: string, values: T): Promise<T> {
        const result = await fetch(url, {
            method: 'POST',
            headers: this.headers(),
            body: JSON.stringify(values),
        });

        return await result.json();
    }

    async put<T>(url: string, id: string, values: T): Promise<T> {
        const result = await fetch(`${url}${id}/`, {
            method: 'PUT',
            headers: this.headers(),
            body: JSON.stringify(values),
        });

        return await result.json();
    }

    async delete(url: string, id: string): Promise<void> {
        const result = await fetch(url + id, {
            method: 'DELETE',
            headers: this.headers()
        });

        return new Promise((resolve, reject) => {
            if (result.status == 204) {
                resolve();
            }
            else {
                reject();
            }
        });
    }
}

class ApiPart {
    protected client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }
}

class ClosingApi extends ApiPart {
    async list(): Promise<Closing[]> {
        return this.client.get(urls.agenda.closing.list);
    }

    async delete(id: string) {
        return this.client.delete(urls.agenda.closing.delete, id);
    }

    async update(id: string, values: Closing) {
        return this.client.put(urls.agenda.closing.add, id, values);
    }

    async create(values: Closing) {
        return this.client.post(urls.agenda.closing.add, values);
    }
}

class BabexApi {
    protected client = new ApiClient();

    agenda = {
        closing: new ClosingApi(this.client)
    }
}

export const babexApi = new BabexApi();
