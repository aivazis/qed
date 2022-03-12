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
export const Up = ({ node }) => {
    // make me a handler that nudges the current node
    const { nudge } = useSetPixelPath()

    // make my controller
    const behaviors = {
        onClick: () => nudge({ node, axis: 0, value: -1 }),
    }

    // render
    return (
        <g transform={`translate(${7 / 8 * 500} 225) scale(${1 / 8})`}>
            <Arrow d={arrow} {...behaviors} />
        </g>
    )
}


const Arrow = styled.path`
    fill: hsl(0deg, 100%, 35%);
    stroke: none;
`

const arrow = "M 0 1000 C 500 500 500 500 1000 1000 L 500 0 Z"


// end of file
