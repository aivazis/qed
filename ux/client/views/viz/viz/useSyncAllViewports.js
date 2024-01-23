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
export const useSyncAllViewports = idx => {
    // grab the sync table mutator from the context
    const { setSynced } = React.useContext(Context)
    // make a handler that creates a new table filled with my state
    const syncAll = () => setSynced(old => {
        // get my current state
        const sync = old[idx]
        // if i'm clearing everybody
        if (sync.scroll === null) {
            // make a new table
            return old.map(entry => ({ ...entry, scroll: null }))
        }
        // otherwise, i must be careful: nulls turn into my state, but existing scroll
        // values should be left alone since they may contain particular offsets
        return old.map(entry => (
            { ...entry, scroll: entry.scroll == null ? sync.scroll : entry.scroll }
        ))
    })
    // and return it
    return syncAll
}


// end of file
