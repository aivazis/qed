// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = theme.page.bright

// paint mixer
const console = (client) => ({
    // the frame
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

    // the prompt and the cursor
    decoration: {
        // inherit
        ...style.decoration,
        // stroke
        stroke: ink,
        strokeWidth: "1px",
        strokeLinecap: "round",
        strokeLinejoin: "round",
        // fill
        fill: "none",
        // plus whatever the {client} said
        ...client?.decoration,
    },
})


// publish
export default {
    console,
}


// end of file
