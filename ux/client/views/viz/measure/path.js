// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// join to anchors with a line
export const Path = ({ points, closed }) => {
    // check whether we have any points yet
    if (points.length === 0) {
        // in which case, bail
        return null
    }
    // otherwise, form the path
    const path = points.reduce(
        (prev, current) => prev + ` L ${current.x} ${current.y}`,
        `M ${points[0].x} ${points[0].y} `
    )
    // the additional tail that specifies whether the path is open or closed
    const tail = closed ? " Z" : ""
    // and render
    return (
        <g>
            <Mat d={path + tail} />
            <Line d={path + tail} />
        </g>
    )
}


// the mat
const Mat = styled.path`
    fill: none;
    stroke: ${() => theme.page.relief};
    stroke-width: 8;
    vector-effect: non-scaling-stroke;
`


// the path
const Line = styled.path`
    fill: none;
    stroke: ${() => theme.page.highlight};
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
`


// end of file
