// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// paint mixer for a {toolbar}
const toolbar = ({ direction, client }) => ({
    // the base layer
    // paint
    backgroundColor: "hsl(0deg, 0%, 12%)",
    // for my children
    display: "flex",
    flexDirection: direction,
    alignItems: "center",

    // plus whatever the client specified
    ...client?.toolbar,
})


// publish
export default {
    toolbar,
}

// end of file
