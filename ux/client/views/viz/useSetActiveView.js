// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useSetActiveView = view => {
    // grab the list of {views} from context
    const { setActiveView } = React.useContext(Context)
    // make a handler that makes {view} the acive one
    const activate = () => {
        // easy enough
        setActiveView(view)
        // all done
        return
    }
    // and return it
    return activate
}


// end of file
