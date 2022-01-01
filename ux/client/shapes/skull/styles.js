// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = "hsl(0deg, 100%, 50%)"
const paint = "hsl(0deg, 100%, 50%)"

// publish
export default {
    // the main shape
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        // fill
        fill: paint,
    },

    // decorative touches
    decoration: {
        // inherit
        ...style.decoration,
    },
}


// end of file
