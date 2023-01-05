// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { usePixelPathSelection } from '../../../viz/usePixelPathSelection'
import { useSetPixelPath } from '../../../viz/useSetPixelPath'
import { useUpdatePixelLocation } from './useUpdatePixelLocation'
// components
import { Arrow } from './arrow'


// nudge the selected {node} upwards
export const Up = () => {
    // pull info out of my context
    const { nudge } = useUpdatePixelLocation()
    // get the current pixel path selection
    const nodes = usePixelPathSelection()
    // make me a handler that moves the current selection
    const { displace } = useSetPixelPath()

    // make my handler
    const move = evt => {
        // unpack the event information
        const { altKey } = evt
        // pick a displacement
        const value = altKey ? -5 : -1
        // nudge the pixel location
        nudge({ dLine: value, dSample: 0 })
        // and the selection, if any
        displace({ nodes, delta: { x: 0, y: value } })
        // all done
        return
    }

    // make my controller
    const behaviors = {
        onClick: move,
    }

    // render
    return (
        <Arrow path={arrow}
            placement={`translate(${9 / 10 * 500} 100) scale(${1 / 10})`}
            behaviors={behaviors} />
    )
}


// the path
const arrow = "M 0 1000 C 500 500 500 500 1000 1000 L 500 0 Z"


// end of file
