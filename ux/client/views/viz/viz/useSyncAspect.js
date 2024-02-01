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
import { useSetPixelPath } from './useSetPixelPath'

// build a handler that toggles the specified entry in the sync table
export const useSyncAspect = () => {
    // grab the sync table setter
    const { setSynced, setMeasureLayer } = React.useContext(Context)
    // and the handler that copies pixel paths
    const { copy } = useSetPixelPath()

    // make a handler factory and return it
    const toggle = (viewport, aspect) => () => {
        // the new value of the aspect
        let value
        // and a path synced viewport
        let src
        // update the sync table
        setSynced(old => {
            // make a copy of the old state
            const clone = old.map(sync => ({ ...sync }))
            // flip the {aspect} of the viewport
            clone[viewport][aspect] = !old[viewport][aspect]
            // remember the new value
            value = clone[viewport][aspect]
            // find a viewport that is path synced; use {old} for the search so i don't bump
            // into myself
            src = old.findIndex(port => port.path)
            // return the new state
            return clone
        })
        // if we are turning on path sync
        if (aspect === "path" && value === true) {
            // turn on the measure layer for this viewport
            setMeasureLayer(old => {
                // make a copy
                const pile = [...old]
                // adjust the entry for this viewport
                pile[viewport] = true
                // and return the bew pile
                return pile
            })
            // if we have a path synced viewport
            if (src >= 0) {
                // copy its pixel path
                copy(src, viewport)
            }
        }
        // all done
        return
    }

    // make a handler factory and return it
    const update = (viewport, aspect) => value => {
        // a path synced viewport
        let src
        // update the sync table
        setSynced(old => {
            // make a copy of the old state
            const clone = [...old]
            // flip the {aspect} of the viewport
            clone[viewport][aspect] = value
            // find a viewport that is path synced; use {old} for the search so i don't bump
            // into myself
            src = old.findIndex(port => port.path)
            // return the new state
            return clone
        })
        // if we are turning on path sync
        if (aspect === "path" && value === true) {
            // turn on the measure layer for this viewport
            setMeasureLayer(old => {
                // make a copy
                const pile = [...old]
                // adjust the entry for this viewport
                pile[viewport] = true
                // and return the bew pile
                return pile
            })
            // if we have a path synced viewport
            if (src >= 0) {
                // copy its pixel path
                copy(src, viewport)
            }
        }
        // all done
        return
    }

    // all done
    return { toggle, update }
}


// end of file
