// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {
    box: {
        fontSize: "60%",
        // colors
        color: theme.header.color,
    },

    entry: {
        cursor: "default",
        verticalAlign: "baseline",
    },

    attribute: {
        fontFamily: "rubik-light",
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
        // style
        fontFamily: "inconsolata",
        color: wheel.gray.aluminum,
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
