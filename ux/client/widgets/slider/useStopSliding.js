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
export const useStopSliding = () => {
    // N.B.: do not be tempted to clear {cursor.current}, the last recorded mouse coordinates;
    //       there is a {pick} that gets processed {onClick} after the {onMouseUp} event fires
    //       so we can't just mess with the cursor here; instead, we record the actual mouse
    //       coordinates so the value is guaranteed to catch up with the mouse

    // grab the mutator of the sliding indicator
    const { cursor, setSliding } = React.useContext(Context)

    // make a handler
    const end = evt => {
        // that clears the flag
        setSliding(null)
        // and records the mouse coordinates
        cursor.current = { x: evt.clientX, y: evt.clientY }
        // all done
        return
    }

    // return the handler
    return end
}


// end of file
