// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { wheel } from '~/palette'

// the base style
import style from '~/shapes/styles'


// the shape color
const ink = wheel.gray.aluminum

// publish
export default {
    // the main shape
    icon: {
        // inherit
        ...style.icon,
        // stroke
        stroke: ink,
        strokeWidth: 1,
        strokeLinecap: "round",
        strokeLinejoin: "round",
        // fill
        fill: "none",
    },
}


// end of file
