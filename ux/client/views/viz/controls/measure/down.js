// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useSetPixelPath } from '../../viz/useSetPixelPath'


// a table of the points on the {measure} layer of the active viewport
export const Down = ({ node }) => {
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
        <g transform={`translate(${7 / 8 * 500} 650) scale(${1 / 8})`}>
            <Arrow d={arrow} {...behaviors} />
        </g>
    )
}


const Arrow = styled.path`
    fill: hsl(0deg, 100%, 35%);
    stroke: none;
`

const arrow = "M 0 0 C 500 500 500 500 1000 0 L 500 1000 Z"


// end of file
