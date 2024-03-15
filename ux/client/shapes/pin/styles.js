// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = theme.page.bright
const paint = theme.page.normal

// paint mixer
const pin = (client) => ({
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
    pin,
}


// end of file
