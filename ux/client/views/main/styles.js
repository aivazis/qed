// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// publish
export default {
    // the overall page
    page: {
        // inherit
        ...base.page,
    },

    // the container
    panel: {
        // inherit
        ...base.panel,
        // style
        // no smaller than
        minWidth: "600px",
        minHeight: "400px",
    },

    activitybar: {
        // NYI
        // NOT STYLABLE FROM HERE AT THIS POINT
        // THE ActivityBar DOES NOT PARTICIPATE IN PAINT MIXING
    },
}


// end of file
