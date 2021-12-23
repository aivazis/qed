// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {

    info: {
        // positioning
        padding: "0.125rem 1.0em",
        // colors
        color: theme.header.color,
        // text
        fontSize: "50%",
        fontFamily: "rubik-light",
        // disable text selection
        userSelect: "none",
        // don't wrap
        overflow: "clip",
        whiteSpace: "nowrap",
    },

    name: {
        textTransform: "uppercase",
    },

    value: {
        color: wheel.gray.aluminum,
    },

    separator: {
        display: "inline-block",
        width: "1.0em",
        textAlign: "center",
    }
}


// end of file
