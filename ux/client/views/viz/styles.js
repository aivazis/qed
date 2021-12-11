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
        // styling
        backgroundColor: "hsl(0deg, 0%, 5%, 1)",
        // for my children
        display: "flex",
        flexDirection: "column",
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
        // set up the preferred initial width
        width: "300px",
        flex: "0 0 auto",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    }
}


// the panel with the rendering controls
const controls = {
    // the panel
    panel: {
        // inherit
        ...flex.panel,
        // set up the preferred initial width
        width: "300px",
        flex: "0 0 auto",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    }
}


// the blank view
const blank = {
    // the container
    nyi: {
        // inherit
        ...base.panel,
    },

    placeholder: {
        position: "relative",
        top: "50%",
        left: "50%",
        width: "100%",
        height: "400px",
        textAlign: "center",
        transform: "translate(-50%, -50%)",
    },

    icon: {
        // placement
        margin: "1.0em auto",
        width: "300px",
        height: "300px",
    },

    shape: {
        icon: {
            // stroke
            stroke: theme.page.name,
            strokeWidth: 3,
            // fill
            fill: "none",
        },
    },

    message: {
        fontFamily: "inconsolata",
        fontSize: "120%",
        textAlign: "center",
    },

}

// publish
export default { flex, datasets, controls, blank }


// end of file
