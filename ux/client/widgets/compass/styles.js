// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get colors
import { theme } from '~/palette'

// pick a highlight
const red = "hsl(0deg,50%,20%)"

// publish
export default {
    panel: {
    },

    north: {
        // stroke
        stroke: theme.page.dim,
        // exclude the stroke from any transforms
        vectorEffect: "non-scaling-stroke",

        // fill
        fill: "none",
    },

    east: {
        // stroke
        stroke: theme.page.dim,
        // exclude the stroke from any transforms
        vectorEffect: "non-scaling-stroke",

        // fill
        fill: "none",
    },

    needle: {
        // stroke
        stroke: red,
        // exclude the stroke from any transforms
        vectorEffect: "non-scaling-stroke",

        // fill
        fill: "none",
    },

    needletip: {
        // stroke
        stroke: "none",
        // just in case we ever stroke this
        vectorEffect: "non-scaling-stroke",

        // fill
        fill: red,
        fillOpacity: "1",
    },
}


// end of file
