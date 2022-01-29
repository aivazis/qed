// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = "hsl(0deg, 0%, 90%)"
const paint = theme.page.background
const badge = "hsl(0deg, 0%, 15%, 1)"

// paint mixer
const live = (client) => ({
    // the main shape
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        strokeWidth: "1px",
        // fill
        fill: "none",
        // plus whatever the {client} said
        ...client?.icon,
    },

    // the badge
    badge: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        strokeWidth: "1px",
        // plus whatever the {client} said
        ...client?.icon,
        // fill unconditionally
        fill: badge,
        fillOpacity: 1.0,
    },

    // decorative touches
    decoration: {
        // inherit
        ...style.decoration,
        // stroke
        stroke: ink,
        strokeWidth: "0.5px",
        // fill
        fill: "none",
        // plus whatever the {client} said
        ...client?.decoration,
    },
})


// publish
export default {
    live,
}


// end of file
