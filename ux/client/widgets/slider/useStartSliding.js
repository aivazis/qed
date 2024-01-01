// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// start choosing a new slider value
export const useStartSliding = () => {
    // grab the mutator of the sliding indicator
    const { cursor, setSliding } = React.useContext(Context)

    // make a handler
    const start = (id, evt) => {
        // that sets the flag
        setSliding(id)
        // and records the raw mouse coordinates
        cursor.current = { x: evt.clientX, y: evt.clientY }
        // all done
        return
    }

    // return the handler
    return start
}


// end of file
