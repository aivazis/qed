// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context, measureDefault, pixelPathDefault, pixelPathSelectionDefault } from './context'


// access to the registered views
export const useSplitView = view => {
    // grab what i need from the context
    const {
        // the list of synced views
        synced,
        // mutators
        setActiveViewport, setViews, setSynced, setZoom,
        setMeasureLayer, setPixelPath, setPixelPathSelection,
        // the ref with the base zoom levels
        baseZoom,
        // the default state of the measure layer
    } = React.useContext(Context)

    // make a handler that adds a new blank view after a given on
    const splitView = () => {

        // add a new view to the pile
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // the new view is a copy of the view being split
            clone.splice(view + 1, 0, old[view])
            // all done
            return clone
        })

        // initialize its sync status
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // clone the sync status for the new viewport
            table.splice(view + 1, 0, synced[view])
            // return the new table
            return table
        })

        // initialize its zoom level
        setZoom(old => {
            // make a copy of the old table
            const table = [...old]
            // add the new viewport at the same zoom level as the current one
            table.splice(view + 1, 0, old[view])
            // all done
            return table
        })

        // maintain the base zoom levels
        baseZoom.current.splice(view + 1, baseZoom.current[view])

        // initialize its measure layer status
        setMeasureLayer(old => {
            // make a copy
            const table = [...old]
            // add a marker for the new viewport
            table.splice(view + 1, 0, measureDefault)
            // and return the new table
            return table
        })
        // make an empty pixel path for it
        setPixelPath(old => {
            // make a copy of the current state
            const table = [...old]
            // add an empty path at the right spot
            table.splice(view + 1, 0, ...pixelPathDefault())
            // and return the new table
            return table
        })
        // and an empty path selection for it
        setPixelPathSelection(old => {
            // make a copy of the current state
            const table = [...old]
            // add an empty path at the right spot
            table.splice(view + 1, 0, ...pixelPathSelectionDefault())
            // and return the new table
            return table
        })


        // activate the new view
        setActiveViewport(view + 1)

        // all done
        return
    }
    // and return it
    return splitView
}


// end of file
