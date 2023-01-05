// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// mark a point
export const Path = ({ points }) => {
    // check whether we have any points yet
    if (points.length === 0) {
        // in which case, bail
        return null
    }
    // otherwise, form the path
    const path = points.reduce(
        (prev, current) => prev + ` L ${current[1]} ${current[0]}`,
        `M ${points[0][1]} ${points[0][0]} `
    )
    // and render
    return (
        <g>
            <Mat d={path} />
            <Line d={path} />
        </g>
    )
}


// the mat
const Mat = styled.path`
    fill: none;
    stroke: hsl(0deg, 0%, 10%, 0.75);
    stroke-width: 8;
    vector-effect: non-scaling-stroke;
`


// the path
const Line = styled.path`
    fill: none;
    stroke: hsl(28deg, 90%, 55%);
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
`


// end of file
