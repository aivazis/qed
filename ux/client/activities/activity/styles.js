// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// grab the base paint mixer
import paint from '../styles'


// mix my paint
const activity = (client) => {
    // my badge overrides
    const badge = {
        // get the base layer
        ...client.badge,
        // enhance selected badges
        selected: {
            // styling
            borderLeft: "2px solid white",
            // plus whatever the client said
            ...client.badge.selected,
        },
    }

    // my shape overrides
    const shape = {
        // for all shapes
        base: {
            // styling
            fillOpacity: 0.5,
            strokeOpacity: 0.5,
            // plus whatever the client wants
            ...client.shape.base,
        },
        // for disabled shapes
        disabled: {
            // styling
            fillOpacity: 0.2,
            strokeOpacity: 0.2,
            // plus whatever the client wants
            ...client.shape.disabled,
        },
        // for selected shapes
        selected: {
            // styling
            fillOpacity: 1.0,
            strokeOpacity: 1.0,
            // plus whatever the client wants
            ...client.shape.selected,
        },
        // for available shapes
        available: {
            // styling
            fillOpacity: 1.0,
            strokeOpacity: 1.0,
            // plus whatever the client wants
            ...client.shape.available,
        },
    }

    // all done
    return { ...client, badge, shape }
}


// publish
export default {
    activity,
}


// end of file
