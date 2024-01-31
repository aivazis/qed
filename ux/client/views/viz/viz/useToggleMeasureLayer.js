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
export const useToggleMeasureLayer = viewport => {
    // grab the measure layer mutator from context
    const { setMeasureLayer } = React.useContext(Context)
    // make handlers that clear the pixel path and the selection
    const { clear: clearPixelPath } = useSetPixelPath(viewport)
    const { clear: clearPixelPathSelection } = useSetPixelPathSelection(viewport)

    // a handler that toggles whether the measure layer is visible
    const toggle = () => {
        // toggle
        setMeasureLayer(old => {
            // make a copy of the measure layer status table
            const table = [...old]
            // toggle the entry that corresponds to this viewport
            table[viewport] = !table[viewport]
            // and return the new table
            return table
        })

        // on toggle, clear the pixel path
        clearPixelPath()
        // and the selection
        clearPixelPathSelection()

        // all done
        return
    }

    // return the toggle
    return toggle
}


// end of file
