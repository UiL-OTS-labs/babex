import {urls, parentUrls} from './urls';
import type {Appointment, Closing, Call} from './types';
import {formatDateISO} from './util';

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

class ApiError extends Error {
    constructor(code: number, message: string) {
        super(`${code} ${message}`);
    }
}

class ApiRequest<T> {
    _promise: Promise<any>;
    _abort: AbortController | null = null;

    constructor(promise: Promise<any>, abort?: AbortController) {
        this._promise = promise;
        if (abort) {
            this._abort = abort;
        }
    }

    cancel() {
        if (this._abort) {
            this._abort.abort();
        }
        else {
            throw new Error("Cannot cancel request");
        }
    }

    success(callback: any) {
        this._promise = this._promise.then(async result => {
            if (result.status >= 400) {
                throw new ApiError(result.status, result.statusText);
            }

            callback(await result.json() as T);
        })
    }

    error(callback: any) {
        this._promise = this._promise.catch(e => {
            callback(e);
        });
    }
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

    get<T>(url: string, params?: Record<string, any>): ApiRequest<T> {
        let u = new URL(url, window.location.href);

        if (params !== undefined) {
            for(let key of Object.keys(params)) {
                if (params[key] !== null) {
                    u.searchParams.append(key, params[key]);
                }
            }
        }

        let abortController = new AbortController();
        let request = new ApiRequest(
            fetch(u.toString(), {
                credentials: 'include',
                method: 'GET',
                headers: this.headers(),
                signal: abortController.signal
            }),
            abortController
        );

        return request;
    }

    post<T, D>(url: string, values: D): ApiRequest<T> {
        let abortController = new AbortController();
        let request =  new ApiRequest(
            fetch(url, {
                credentials: 'include',
                method: 'POST',
                headers: this.headers(),
                body: JSON.stringify(values),
                signal: abortController.signal
            }),
            abortController
        );

        return request;
    }

    put<T, D>(url: string, id: string, values: D): ApiRequest<T> {
        let abortController = new AbortController();
        let request = new ApiRequest(
            fetch(`${url}${id}/`, {
                credentials: 'include',
                method: 'PUT',
                headers: this.headers(),
                body: JSON.stringify(values),
                signal: abortController.signal
            }),
            abortController);

        return request;
    }

    delete(url: string, id: string): ApiRequest<void> {
        let result = fetch(url + id, {
            credentials: 'include',
            method: 'DELETE',
            headers: this.headers()
        });

        return new ApiRequest(new Promise<void>(async (resolve, reject) => {
            if ((await result).status == 204) {
                resolve();
            }
            else {
                reject();
            }
        }));
    }

    patch<T, D>(url: string, id: string, values: D): ApiRequest<T> {
        let abortController = new AbortController();
        let request = new ApiRequest(fetch(`${url}${id}/`, {
            credentials: 'include',
            method: 'PATCH',
            headers: this.headers(),
            body: JSON.stringify(values),
            signal: abortController.signal
        }), abortController);

        return request;
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

    async list(): Promise<ApiRequest<T[]>> {
        return this.client.get(this.endpoint);
    }

    async delete(id: string) {
        return this.client.delete(this.endpoint, id);
    }

    async update(id: string, values: T) {
        return this.client.put(this.endpoint, id, values);
    }

    async updatePartial(id: string, values: Partial<T>) {
        return this.client.patch(this.endpoint, id, values);
    }

    async create(values: T) {
        return this.client.post(this.endpoint, values);
    }

    async createMany(values: T[]) {
        return this.client.post(this.endpoint, values);
    }
}


interface AppointmentCreate {
    start: Date,
    end: Date,
    experiment: number,
    leader: number,
    participant: number,
}

interface AppointmentEmail {
    content: string
}

interface AppointmentSendEmail {
    id: number,  // appointment id
    content: string
}

class BabexApi {
    protected client = new ApiClient();

    agenda = {
        closing: new GenericApiPart<Closing>(this.client, urls.agenda.closing),
        appointment: new GenericApiPart<Appointment>(this.client, urls.agenda.appointment),
    }

    call = {
        appointment: {
            create: (data: AppointmentCreate) => {
                return this.client.post<Appointment, AppointmentCreate>(urls.call.appointment, data);
            },
            getEmail: (id: number) => {
                return this.client.get<AppointmentEmail>(urls.call.sendEmail + id);
            },
            sendEmail: (data: AppointmentSendEmail) => {
                return this.client.post(urls.call.sendEmail, data);
            },
        },
        log: new GenericApiPart<Call>(this.client, urls.call.log),
    }

    participants = {
        demographics: {
            get: (date: Date, experiment?: number) => {
                let dateStr = date ? formatDateISO(date) : '';
                return this.client.get(urls.participants.demographics , {date: dateStr, experiment});
            }
        }
    }
}


// TODO: maybe move to a separate module
class ParentApi {
    protected client = new ApiClient();
    survey = {
        response: new GenericApiPart(this.client, parentUrls.survey.response),
    }
}

export const babexApi = new BabexApi();
export const parentApi = new ParentApi();
