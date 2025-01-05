// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useSetActiveView = () => {
    // grab the view manipulator
    const { activeViewport, setViews } = React.useContext(Context)

    // make the handler
    const activate = (view, viewport = activeViewport) => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the target entry
            clone[viewport] = { ...old[viewport], ...view }
            // and hand off the new state
            return clone
        })
        // all done
        return
    }

    // and return it
    return activate
}


// end of file
