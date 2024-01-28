// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// build a handler that toggles the specified entry in the sync table
export const useToggleSyncedAspect = () => {
    // grab the setter
    const { setSynced } = React.useContext(Context)
    // and return it
    return (viewport, aspect) => () => {
        // update the sync table
        setSynced(old => {
            // make a copy of the old state
            const clone = old.map(sync => ({ ...sync }))
            // flip the {aspect} of the viewport
            clone[viewport][aspect] = !old[viewport][aspect]
            // and return the new state
            return clone
        })
    }
}

// build a handler that sets the specified entry in the sync table to a specific value
export const useSetSyncedAspect = () => {
    // grab the setter
    const { setSynced } = React.useContext(Context)
    // and return it
    return (viewport, aspect) => value => {
        // update the sync table
        setSynced(old => {
            // make a copy of the old state
            const clone = [...old]
            // flip the {aspect} of the viewport
            clone[viewport][aspect] = value
            // and return the new state
            return clone
        })
    }
}


// end of file
