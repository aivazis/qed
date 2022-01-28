// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// the flex container
const flex = {
    // the overall flex container
    box: {
        flex: "1 1 100%",
        minWidth: "800px", // DO NOT REMOVE THIS; IT FORCES flex TO LOOK AT THE WIDTH OF THE PANEL
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
        handle: {},
    },
}

// the activity panels
const activityPanels = {
    // the panel
    panel: {
        // inherit
        ...flex.panel,
        // make it stand out a bit
        backgroundColor: "hsl(0deg, 0%, 7%, 1)",
        // shut flex down for this panel
        flex: "0 0 auto",
        // and set up the preferred initial width
        width: "350px",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    },

    header: {
        // make it stand out a bit
        backgroundColor: "hsl(0deg, 0%, 7%, 1)",
    },
}


// publish
export default {
    activityPanels,
    flex,
}


// end of file
