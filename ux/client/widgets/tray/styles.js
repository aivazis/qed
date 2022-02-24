// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'


// publish
export default {
    // the overall container
    box: {
        // for me
        minHeight: "1.3rem",
        // for my children
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
    },

    // the tray header
    header: {
        // style
        fontSize: "60%",
        padding: "0.25rem 0.0rem 0.25rem 0.6rem",
        cursor: "pointer",
        // colors
        color: "hsl(0deg, 0%, 60%, 1)",
        backgroundColor: "hsl(0deg, 0%, 25%, 1)",
        // don't stretch me
        flex: "0",

        // for my children
        display: "flex",
        alignItems: "center",
    },

    // the tray title
    title: {
        // style
        fontFamily: "rubik-medium",
        padding: "0.0rem 0.0rem 0.0rem 0.5rem",
        // disable text selection
        userSelect: "none",
    },

    // the container of the children
    items: {
        // i stretch
        flex: "1",
        // gimme some room
        padding: "0.25rem 0.0rem",
        // for my children
        display: "flex",
        flexDirection: "column",
        overflow: "auto",
    },
}


// end of file
