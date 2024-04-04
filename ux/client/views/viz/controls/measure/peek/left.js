// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useAnchorMove } from '~/views/viz/measure'
import { useUpdatePixelLocation } from './useUpdatePixelLocation'
// components
import { Arrow } from './arrow'


// nudge the selected {node} to the left
export const Left = ({ viewport, view, handle, deltas }) => {
    // pull info out of my context
    const { nudge } = useUpdatePixelLocation(view)
    // make me a handler that moves the current selection
    const { move } = useAnchorMove(viewport)

    // make my handler
    const bump = evt => {
        // unpack the event information
        const { altKey, shiftKey } = evt
        // encode the modifiers into an index
        const index = (altKey ? 1 : 0) + (shiftKey ? 2 : 0)
        // pick a displacement
        const value = -deltas[index]
        // nudge the pixel location
        nudge({ dx: value, dy: 0 })
        // if there is a selection
        if (handle != null) {
            // update the server side store
            move({ handle, delta: { x: value, y: 0 } })
        }
        // all done
        return
    }

    // make my controller
    const behaviors = {
        onClick: bump,
    }

    // render
    return (
        <Arrow path={arrow}
            placement={`translate(100 ${9 / 10 * 500}) scale(${1 / 10})`}
            behaviors={behaviors} />
    )
}


// the path
const arrow = "M 1000 0 C 500 500 500 500 1000 1000 L 0 500 Z"


// end of file
