// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// update the session id of the given viewport
export const useSetVizSession = viewport => {
    // grab the active viewport and the registered views
    const { activeViewport, setViews } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport

    // a handler that sets the zoom level of the active viewport
    const set = session => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry that corresponds to {viewport}
            clone[viewport] = { ...old[viewport], session }
            // and hand off the new state
            return clone
        })
        // all done
        return
    }

    // return the handler
    return set
}


// end of file
