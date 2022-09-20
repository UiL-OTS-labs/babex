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

interface Call {
    id: number,
    experiment: number,
    participant: number,
    status: string,
    comment: string
}

export {Appointment, Closing, Location, Call};
