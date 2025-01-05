// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get colors
import { theme } from '~/palette'


// publish
export default {
    // the link
    action: {
        // size
        flex: "none",
    },

    // the container
    box: {
        // size
        width: "2em",
        height: "2em",
    },

    // the shape
    shape: {
        fill: theme.page.danger,
        stroke: "none",
    },
}


// end of file
