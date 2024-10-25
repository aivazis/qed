// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = "hsl(0deg, 0%, 40%)"
const highlight = "hsl(0deg, 0%, 20%)"
const paint = "hsl(0deg, 0%, 15%)"

// publish
export default {
    // the main shape
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        strokeWidth: 2,
        // fill
        fill: paint,
    },

    // decorative touches
    decoration: {
        // inherit
        ...style.decoration,
        // stroke
        stroke: highlight,
        strokeWidth: 2,
        // fill
        fill: "none",
    },
}


// end of file
