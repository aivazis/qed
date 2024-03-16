// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// project
// colors
import { theme } from "~/palette"

// the flex container
const flex = {
    // the overall flex container
    box: {
        flex: "1 1 100%",
        minWidth: "800px", // DO NOT REMOVE THIS; IT FORCES flex TO LOOK AT THE WIDTH OF THE PANEL
        backgroundColor: theme.page.relief,
    },

    // individual panels
    panel: {
        // styling
        backgroundColor: theme.page.background,
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
        backgroundColor: theme.page.shaded,
        // shut flex down for this panel
        flex: "0 0 auto",
        // and set up the preferred initial width
        width: "400px",
        // show scroll bars when we run out of room
        overflow: "auto",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    },

    header: {
        // make it stand out a bit
        backgroundColor: theme.page.shaded,
    },
}


// publish
export default {
    activityPanels,
    flex,
}


// end of file
