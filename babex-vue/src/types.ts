import { Dictionary } from "@fullcalendar/core";

interface Appointment {
    id?: number,
    start: Date,
    end: Date,
    participant: string,
    location: string,
    comment: string
    experiment?: string,
    leader?: string,
}

interface Closing {
    id?: number,
    start: Date,
    end: Date,
    is_global: boolean,
    location: number,
    location_name?: string,
    comment: string
}

// TODO Move this in the interface of Appointment and Closing
interface Location {
    id: number,
    name: string
}

interface Call {
    id?: number,
    experiment?: number,
    participant?: number,
    status?: string,
    comment?: string
}

interface ActionContext {
    calendar?: any,
    type?: string,
    event?: Dictionary,
    locations?: Location[],

    start?: Date,
    end?: Date
}

interface User {
    name: string,
    isStaff: boolean
}


export {Appointment, Closing, Location, Call, ActionContext, User};
