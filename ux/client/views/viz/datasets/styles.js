// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// project
// get colors
import { theme } from '~/palette'
// the base styling for children of the {viz} panel
import styles from '../viz/styles'


// my header
const header = {
    // inherit
    ...styles.activityPanels.header
}

const save = {
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
            stroke: theme.page.dim,
        },
        enabled: {
            // pick a color
            stroke: theme.page.normal,
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
            fill: theme.page.dim,
        },
        enabled: {
            // pick a color
            fill: theme.page.normal,

        },
        selected: {},
        available: {
            // pick a color
            fill: theme.page.highlight,

        },
    },
}

// publish
export default {
    header, save,
}

// end of file
