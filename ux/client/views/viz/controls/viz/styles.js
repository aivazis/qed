// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme, wheel } from '~/palette'
// and the base styles
import styles from '../styles'


// common paint for my badges, in normal form
const badge = {
    // the icon container
    badge: {
        base: {
            // for me
            flex: "0 0 auto",
            padding: "0.0rem 0.5rem",
            cursor: "pointer",
            // for my children
            display: "flex",
            alignItems: "center",
        },
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },

    // for the shape container
    shape: {
        base: {},
        disabled: {},
        enabled: {
            // dim it a bit
            strokeOpacity: 0.5,
            fillOpacity: 0.5,
        },
        selected: {},
        available: {
            // full intensity
            strokeOpacity: 1.0,
            fillOpacity: 1.0,
        },
    },

    // for the icon main features
    icon: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },

    // for the icon decoration
    decoration: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },
}


// the button that resets the state
const reset = {
    // inherit
    ...badge,

    badge: {
        ...badge.badge,
        base: {
            ...badge.badge.base,
            // for me
            justifySelf: "end",
        },
    },

    icon: {
        ...badge.icon,
        selected: {
            ...badge.icon.selected,
            stroke: theme.page.name,
        },
        available: {
            ...badge.icon.available,
            stroke: theme.page.name,
        },
    },

    decoration: {
        ...badge.decoration,
        selected: {
            ...badge.decoration.selected,
            stroke: "none",
            fill: theme.page.name,
        },
        available: {
            ...badge.decoration.available,
            stroke: "none",
            fill: theme.page.name,
        },
    }
}


// publish
export default {
    reset,
}


// end of file
