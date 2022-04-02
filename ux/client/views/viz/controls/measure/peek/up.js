// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Arrow } from './arrow'
// hooks
import { useSetPixelPath } from '../../../viz/useSetPixelPath'


// nudge the selected {node} upwards
export const Up = ({ node }) => {
    // make me a handler that nudges the current node
    const { nudge } = useSetPixelPath()

    // make my handler
    const move = evt => {
        // unpack the event information
        const { altKey } = evt
        // pick a displacement
        const value = altKey ? 5 : 1
        // if the
        // nudge
        nudge({ node, axis: 0, value })
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
            placement={`translate(${7 / 8 * 500} 225) scale(${1 / 8})`}
            behaviors={behaviors} />
    )
}


// the path
const arrow = "M 0 1000 C 500 500 500 500 1000 1000 L 500 0 Z"


// end of file
