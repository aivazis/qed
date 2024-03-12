// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'
import { useSetPixelPath } from './useSetPixelPath'
import { useSetPixelPathSelection } from './useSetPixelPathSelection'


// toggle the measure layer over this viewport
export const useSetMeasureLayer = viewport => {
    // grab the measure layer mutator from context
    const { setMeasureLayer, setSynced } = React.useContext(Context)
    // make handlers that clear the pixel path and the selection
    const { clear: clearPixelPath } = useSetPixelPath(viewport)
    const { clear: clearPixelPathSelection } = useSetPixelPathSelection(viewport)

    // a handler that ses the visibility of the measure layer
    const set = (value, port = viewport) => {
        // toggle
        setMeasureLayer(old => {
            // make a copy of the measure layer status table
            const table = [...old]
            // adjust the entry that corresponds to this viewport
            table[port] = value
            // all done; return the new table
            return table
        })

        // on toggle, clear the pixel path
        clearPixelPath(port)
        // and the selection
        clearPixelPathSelection(port)

        // if we are turning off the measure layer
        if (value === false) {
            // we clear path syncing
            setSynced(old => {
                // make a copy of the old state
                const pile = old.map(sync => ({ ...sync }))
                // clear the path sync of my {port}
                pile[port].path = false
                // and return the new state
                return pile
            })
        }

        // all done
        return
    }

    // a handler that toggles whether the measure layer is visible
    const toggle = (port = viewport) => {
        // the new value of the flag
        let value
        // toggle
        setMeasureLayer(old => {
            // make a copy of the measure layer status table
            const table = [...old]
            // toggle the entry that corresponds to this viewport
            table[port] = !table[port]
            // remember the new value
            value = table[port]
            // all done; return the new table
            return table
        })

        // on toggle, clear the pixel path
        clearPixelPath(port)
        // and the selection
        clearPixelPathSelection(port)

        // if we turned off the measure layer
        if (value === false) {
            // we also clear path syncing
            setSynced(old => {
                // make a copy of the old state
                const pile = old.map(sync => ({ ...sync }))
                // clear the path sync of my {port}
                pile[port].path = false
                // and return the new state
                return pile
            })
        }

        // all done
        return
    }

    // return the handlers
    return { set, toggle }
}


// end of file
