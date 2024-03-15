// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const tray = "hsl(0deg, 0%, 60%)"
const arrow = "hsl(0deg, 100%, 60%)"

// publish
export default {
    // the main shape
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: tray,
        strokeWidth: 1,
        // fill
        fill: tray,
    },

    decoration: {
        // inherit
        ...style.decoration,
        // stroke
        stroke: arrow,
        strokeWidth: 1,
        // fill
        fill: arrow,
    },
}


// end of file
