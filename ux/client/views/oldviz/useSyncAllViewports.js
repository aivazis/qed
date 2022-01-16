// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// toggle the sync status of this viewport
export const useSyncAllViewports = idx => {
    // grab the sync table mutator from the context
    const { setSynced } = React.useContext(VizContext)
    // make a handler that created new table filled with my state
    const syncAll = () => setSynced(old => new Array(old.length).fill(old[idx]))
    // and return it
    return syncAll
}


// end of file
