// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'

// publish
export default {
    // exclude the stroke from any transforms
    vectorEffect: "non-scaling-stroke",

    // shapes have two parts:
    //
    //  - icon:       the main graphic
    //  - decoration: decorative highlights and detail
    //
    icon: {
        // stroke
        strokeWidth: 0.5,
        // exclude the stroke from any transforms
        vectorEffect: "non-scaling-stroke",
    },

    decoration: {
        // stroke
        strokeWidth: 0.25,
        // fill
        fill: "none",
        // exclude the stroke from any transforms
        vectorEffect: "non-scaling-stroke",
    },
}


// end of file
