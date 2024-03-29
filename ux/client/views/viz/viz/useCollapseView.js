// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import {
    Context,
    emptyView, syncedDefault, zoomDefault,
    measureDefault, pixelPathDefault, pixelPathSelectionDefault,
} from './context'


// remove a viewport
export const useCollapseView = () => {
    // grab the list of {views} from context
    const {
        // the active viewport
        activeViewport,
        // mutators
        setActiveViewport, setViews, setSynced, setZoom,
        setMeasureLayer, setPixelPath, setPixelPathSelection,
        // the ref with the base zoom levels
        baseZoom,
    } = React.useContext(Context)
    // make a handler that removes a viewport
    const collapseView = viewport => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone.splice(viewport, 1)
            // if i'm left with an empty pile
            if (clone.length === 0) {
                // reinitialize
                return [emptyView()]
            }
            // and hand off the new state
            return clone
        })

        // remove its flag from the sync table
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // remove the status of the current view
            table.splice(viewport, 1)
            // if i'm left with an empty pile
            if (table.length === 0) {
                // reinitialize
                return [syncedDefault]
            }
            // return the new table
            return table
        })

        // remove its zoom level from the table
        setZoom(old => {
            // make a copy of the old table
            const table = [...old]
            // remove the zoom level of the current view
            table.splice(viewport, 1)
            // if i'm left with an empty pile
            if (table.length === 0) {
                // reinitialize
                return [zoomDefault]
            }
            // otherwise, return the new table
            return table
        })

        // maintain the base zoom level table
        const bz = baseZoom.current
        // remove the entry for the current view
        bz.splice(viewport, 1)
        // if this leaves us with an empty table
        if (bz.length == 0) {
            // reinitialize
            baseZoom.current = [zoomDefault]
        }

        // remove the measure layer status of the collapsing viewport
        setMeasureLayer(old => {
            // make a copy
            const table = [...old]
            // remove the marker for the collapsing viewport
            table.splice(viewport, 1)
            // if this leaves us with nothing
            if (table.length === 0) {
                // reinitialize
                return [measureDefault]
            }
            // and return the new table
            return table
        })
        // make an empty pixel path for it
        setPixelPath(old => {
            // make a copy of the current state
            const table = [...old]
            // remove the pixel path of the collapsing view
            table.splice(viewport, 1)
            // if this leaves us with nothing
            if (table.length === 0) {
                // reinitialize
                return [pixelPathDefault()]
            }
            // and return the new table
            return table
        })
        // and an empty path selection
        setPixelPathSelection(old => {
            // make a copy of the current state
            const table = [...old]
            // remove the pixel path of the collapsing view
            table.splice(viewport, 1)
            // if this leaves us with nothing
            if (table.length === 0) {
                // reinitialize
                return [pixelPathSelectionDefault()]
            }
            // and return the new table
            return table
        })

        // if the active viewport has collapsed ot the active viewport is after the collapsed one on
        // the pile
        if (viewport <= activeViewport) {
            // activate the previous one
            setActiveViewport(Math.max(viewport - 1, 0))
        }

        // all done
        return
    }
    // and return it
    return collapseView
}


// end of file
