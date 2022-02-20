// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// start choosing a new slider value
export const useStartPicking = () => {
    // grab the mutator of the picking indicator
    const { setPicking } = React.useContext(Context)

    // make a handler
    const start = () => {
        // that sets the flag
        setPicking(true)
        // all done
        return
    }

    // return the handler
    return start
}


// end of file
