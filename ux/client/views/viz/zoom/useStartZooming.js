// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the zoom level of the active viewport
export const useStartZooming = () => {
    // grab the mutator of the zooming indicator
    const { setZooming } = React.useContext(Context)

    // make a handler
    const start = () => {
        // that sets the flag
        setZooming(true)
        // all done
        return
    }

    // return the handler
    return start
}


// end of file
