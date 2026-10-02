// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the cells of the grid, as the corners of their squares, and whether each is filled
const cells = [
    [140, 140, true], [400, 140, true], [660, 140, false],
    [140, 400, true], [400, 400, false], [660, 400, false],
    [140, 660, false], [400, 660, false], [660, 660, true],
]


// render the shape: a chunk grid, some of whose cells hold data
export const Quality = ({ style }) => {
    // mix my paint
    const paint = styles.quality(style)

    // paint me
    return (
        <>
            {cells.map(([x, y, filled]) => (
                // each cell is a square, outlined or filled
                <rect key={`${x}-${y}`} x={x} y={y} width="200" height="200" rx="20" ry="20"
                    style={filled ? paint.decoration : paint.icon} />
            ))}
        </>
    )
}


// end of file
