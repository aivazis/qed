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
const paint = theme.page.normal

// publish
export default {
    // the frame
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        // fill
        fill: paint,
    },

    // the prompt and the cursor
    decoration: {
        // inherit
        ...style.decoration,
        // stroke
        stroke: ink,
        // fill
        fill: ink,
    },
}


// end of file
