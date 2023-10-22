// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// build a handler that activates a specific viewport
export const useSetActiveViewport = () => {
    // grab the list of {views} from context
    const { setActiveViewport } = React.useContext(Context)
    // build a handler that makes {viewport} the active one
    const activate = (viewport) => {
        // all done
        return () => setActiveViewport(viewport)
    }
    // and return it
    return activate
}


// end of file
