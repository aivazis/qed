// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the logo is a wordmark, much wider than it is tall, and it names the app, so it is drawn almost
// twice the size of the other activities, in a badge padded to be as wide as the others, and
// brighter than they are at rest, leaving room for the highlight when the pointer is over it
const activity = client => ({
    // everything the client asked for
    ...client,
    // and a badge that gives the logo the width of the bar
    badge: {
        ...client?.badge,
        base: {
            ...client?.badge?.base,
            padding: "0 2px",
        },
    },
    // with a logo that fades less than the other activities at rest
    shape: {
        ...client?.shape,
        base: {
            ...client?.shape?.base,
            fillOpacity: 0.8,
            strokeOpacity: 0.8,
        },
    },
})

// the size of the logo, relative to the other activities
const scale = 1.8


// publish
export default {
    activity,
    scale,
}


// end of file
