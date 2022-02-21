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
export const useStartSliding = () => {
    // grab the mutator of the sliding indicator
    const { setSliding } = React.useContext(Context)

    // make a handler
    const start = () => {
        // that sets the flag
        setSliding(true)
        // all done
        return
    }

    // return the handler
    return start
}


// end of file
