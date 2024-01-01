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
    // make a handler that created new table filled with my state
    const syncAll = () => setSynced(old => new Array(old.length).fill(old[idx]))
    // and return it
    return syncAll
}


// end of file
