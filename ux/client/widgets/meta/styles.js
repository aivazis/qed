// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {
    box: {},

    entry: {
        cursor: "default",
        lineHeight: "150%",
        verticalAlign: "baseline",
    },

    attribute: {
        textTransform: "uppercase",
        textAlign: "right",
        padding: "0.0em 0.0em 0.0em 0.5em",
        width: "30%",
    },

    separator: {
        width: "1.0em",
        padding: "0.0em 0.25em 0.0em 0.25em",
        textAlign: "center",
    },

    value: {
        // layout
        padding: "0.0em 0.5em 0.0em 0.0em",
        // for my children
        textAlign: "left",
        textOverflow: "ellipsis",
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
    },

}


// end of file
