// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the moving indicator
export const useAnchorDrag = () => {
    // get the flag
    const { dragging, setDragging } = React.useContext(Context)

    // start dragging an anchor
    const start = anchor => {
        // set the flag
        setDragging(anchor)
    }

    // make a handler that clears the movement indicator
    const stop = () => {
        // clear the flag
        setDragging(null)
        // all done
        return
    }

    // all done
    return { start, dragging, stop }
}


// end of file
