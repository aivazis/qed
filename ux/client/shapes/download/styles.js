// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const tray = theme.page.normal
const arrow = theme.page.normal

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
