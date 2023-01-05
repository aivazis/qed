// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook that adjusts the contents of a given viewport
// currently, only called by {reader} instances when selected/updated
export const useVisualize = () => {
    // grab the active viewport index and the {views} mutator
    const { activeViewport, setViews } = React.useContext(Context)

    // make the handler
    const visualize = (view, viewport = activeViewport) => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone[viewport] = { ...old[viewport], ...view }
            // and hand off the new state
            return clone
        })

        // all done
        return
    }

    // and return it
    return visualize
}


// end of file
