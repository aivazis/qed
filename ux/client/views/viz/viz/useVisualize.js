// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook to pull the dataset readers out the outlet context
export const useVisualize = () => {
    // grab the readers
    const { activeViewport, setViews, setSynced } = React.useContext(Context)

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

        // initialize its sync status
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // add the new viewport at {idx} with a default state
            table[viewport] = false
            // return the new table
            return table
        })

        // all done
        return
    }

    // and return it
    return visualize
}


// end of file
