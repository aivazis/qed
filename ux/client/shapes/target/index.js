// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the path data
const hairs = `
    M 500 0 l 0 400
    M 0 500 l 400 0
    M 500 1000 l 0 -400
    M 1000 500 l -400 0
`

// render the shape
export const Target = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <g>
            <circle cx="500" cy="500" r="350" style={ico} />
            <path d={hairs} style={ico} />
        </g>
    )
}


// end of file
