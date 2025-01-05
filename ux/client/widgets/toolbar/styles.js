// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {
    // styling the overall container
    box: {
        // paint
        backgroundColor: theme.page.relief,

        // for my children
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
    },

}


// end of file
