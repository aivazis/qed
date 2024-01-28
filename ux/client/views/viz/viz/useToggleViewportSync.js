// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the sync status of this viewport
export const useToggleViewportSync = idx => {
    // grab the sync table mutator from the context
    const { setSynced } = React.useContext(Context)

    // a handler that toggles whether this viewport is synced to the global camera
    const toggle = () => {
        // update the sync table
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // get my sync state
            const sync = old[idx]
            // flip the scroll status of the specified viewport
            table[idx] = { ...sync, scroll: !sync.scroll }
            // return the new table
            return table
        })
        // all done
        return
    }

    // return the toggle
    return toggle
}


// end of file
