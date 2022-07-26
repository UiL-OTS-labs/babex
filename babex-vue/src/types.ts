interface Appointment {
    start: Date,
    end: Date,
    experiment: string,
    leader: string,
    participant: string,
    location: string,
}

interface Closing {
    start: Date,
    end: Date,
    is_global: boolean,
    location: number,
    location_name: string,
    comment: string
}

interface Location {
    id: number,
    name: string
}

export {Appointment, Closing, Location};
