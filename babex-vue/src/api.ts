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
            credentials: 'include',
            method: 'GET',
            headers: this.headers()
        });

        return await result.json();
    }

    async post<T>(url: string, values: T): Promise<T> {
        const result = await fetch(url, {
            credentials: 'include',
            method: 'POST',
            headers: this.headers(),
            body: JSON.stringify(values),
        });

        return await result.json();
    }

    async put<T>(url: string, id: string, values: T): Promise<T> {
        const result = await fetch(`${url}${id}/`, {
            credentials: 'include',
            method: 'PUT',
            headers: this.headers(),
            body: JSON.stringify(values),
        });

        return await result.json();
    }

    async delete(url: string, id: string): Promise<void> {
        const result = await fetch(url + id, {
            credentials: 'include',
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


class GenericApiPart<T> extends ApiPart {
    protected endpoint: string;

    constructor(client: ApiClient, endpoint: string) {
        super(client);
        this.endpoint = endpoint;
    }

    async list(): Promise<T[]> {
        return this.client.get(this.endpoint);
    }

    async delete(id: string) {
        return this.client.delete(this.endpoint, id);
    }

    async update(id: string, values: T) {
        return this.client.put(this.endpoint, id, values);
    }

    async create(values: T) {
        return this.client.post(this.endpoint, values);
    }
}


class BabexApi {
    protected client = new ApiClient();

    agenda = {
        closing: new GenericApiPart<Closing>(this.client, urls.agenda.closing),
    }
}

export const babexApi = new BabexApi();
