// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme, wheel } from '~/palette'


// paint
const reset = {
    // the icon container
    badge: {
        base: {
            // for me
            flex: "0 0 auto",
            padding: "0.0rem 0.5rem",
            justifySelf: "end",
            // for my children
            display: "flex",
            alignItems: "center",
        },
        disabled: {
            cursor: "default",
        },
        enabled: {
            cursor: "pointer",
        },
        selected: {},
        available: {
            cursor: "pointer",
        },
    },

    // for the shape container
    shape: {
        base: {},
        disabled: {
            // dim it a bit
            fillOpacity: 0.5,
            strokeOpacity: 0.5,
        },
        enabled: {
            // full brightness
            strokeOpacity: 1.0,
            fillOpacity: 1.0,
        },
        selected: {},
        available: {
            // full brightness
            strokeOpacity: 1.0,
            fillOpacity: 1.0,
        },
    },

    // for the icon main features
    icon: {
        base: {
            fill: "none",
        },
        disabled: {
            // pick a color
            stroke: wheel.gray.aluminum,
        },
        enabled: {
            // pick a color
            stroke: wheel.gray.aluminum,
        },
        selected: {},
        available: {
            // pick a color
            stroke: theme.page.name,

        },
    },

    // for the icon decoration
    decoration: {
        base: {
            stroke: "none",
        },
        disabled: {
            // pick a color
            fill: wheel.gray.aluminum,
        },
        enabled: {
            // pick a color
            fill: wheel.gray.aluminum,

        },
        selected: {},
        available: {
            // pick a color
            fill: theme.page.name,

        },
    },
}


// publish
export default {
    reset,
}


// end of file
