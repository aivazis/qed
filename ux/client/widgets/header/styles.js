// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {
    // for me
    display: "flex",
    // text
    fontSize: "60%",
    fontFamily: "rubik-medium",
    textTransform: "uppercase",

    // positioning
    padding: "0.5rem 0.5rem 0.5rem 1.0rem",

    // colors
    color: theme.header.color,
    backgroundColor: theme.header.background,

    // disable text selection
    userSelect: "none",
}


// end of file
