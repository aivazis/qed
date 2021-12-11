// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// the container
const flex = {
    // the overall flex container
    box: {
        flex: "1 1 auto",
        backgroundColor: "hsl(0deg, 0%, 10%)",
    },

    // individual panels
    panel: {
        backgroundColor: "hsl(0deg, 0%, 5%, 1)",
    },

    // the inter-panel separator
    separator: {
        // the line
        rule: {
            backgroundColor: "hsl(0deg, 0%, 15%, 0.5)",
        },
        // the handle
        handle: {
        },
    },
}

// the panel with the known datasets
const datasets = {
    // the panel
    panel: {
        // inherit
        ...flex.panel,
        // colors
        backgroundColor: "hsl(0deg, 0%, 5%, 1)",
        // set up the preferred initial width
        width: "300px",
        flex: "0 0 auto",
        // for my children
        display: "flex",
        flexDirection: "column",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    }
}


// publish
export default { flex, datasets }


// end of file
