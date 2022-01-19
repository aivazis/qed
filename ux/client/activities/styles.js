// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// paint mixer

// for the toolbar
const toolbar = (client) => ({
    // make sure i have the right structure regardless of {client} opinions
    ...client?.toolbar,
})


// for the activities
const activity = (client) => ({
    // the badge
    badge: {
        base: {
            ...client?.badge?.base
        },
        disabled: {
            ...client?.badge?.disabled
        },
        enabled: {
            ...client?.badge?.enabled
        },
        selected: {
            ...client?.badge?.selected
        },
        available: {
            ...client?.badge?.available
        },
    },

    // the shape
    shape: {
        base: {
            ...client?.shape?.base
        },
        disabled: {
            ...client?.shape?.disabled
        },
        enabled: {
            ...client?.shape?.enabled
        },
        selected: {
            ...client?.shape?.selected
        },
        available: {
            ...client?.shape?.available
        },
    },

    // the shape main features, from {~/shapes}
    icon: {
        base: {
            ...client?.icon?.base
        },
        disabled: {
            ...client?.icon?.disabled
        },
        enabled: {
            ...client?.icon?.enabled
        },
        selected: {
            ...client?.icon?.selected
        },
        available: {
            ...client?.icon?.available
        },
    },

    // the shape detailing, form {~/shapes}
    decoration: {
        base: {
            ...client?.decoration?.base
        },
        disabled: {
            ...client?.decoration?.disabled
        },
        enabled: {
            ...client?.decoration?.enabled
        },
        selected: {
            ...client?.decoration?.selected
        },
        available: {
            ...client?.decoration?.available
        },
    },
})

// publish
export default {
    activity,
    toolbar,
}


// end of file
