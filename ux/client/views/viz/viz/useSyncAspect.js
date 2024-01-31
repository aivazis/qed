// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'
// hooks
import { useSetMeasureLayer } from './useSetMeasureLayer'


// build a handler that toggles the specified entry in the sync table
export const useToggleSyncedAspect = () => {
    // grab the sync table setter
    const { setSynced } = React.useContext(Context)
    // and the measure layer control
    const { set } = useSetMeasureLayer()
    // and return it
    return (viewport, aspect) => () => {
        // update the sync table
        setSynced(old => {
            // make a copy of the old state
            const clone = old.map(sync => ({ ...sync }))
            // flip the {aspect} of the viewport
            clone[viewport][aspect] = !old[viewport][aspect]
            // if we are turning on path sync
            if (aspect === "path" && clone[viewport][aspect] === true) {
                // turn on the measure layer for this viewport
                set(true, viewport)
            }
            // return the new state
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
