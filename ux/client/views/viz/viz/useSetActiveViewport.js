// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useSetActiveViewport = () => {
    // grab the list of {views} from context
    const { setActiveViewport } = React.useContext(Context)
    // build a handler that makes {view} the active one
    const activate = (view) => {
        // all done
        return () => setActiveViewport(view)
    }
    // and return it
    return activate
}


// end of file
