// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
import styles from './styles'


// an open padlock; the geometry follows the unlocked icon of the feather set (MIT), drawn at 80% of the box
// the rounded body
const body = `
M 266.7 466.7 L 733.3 466.7 Q 800.0 466.7 800.0 533.3 L 800.0 766.7 Q 800.0 833.3 733.3 833.3 L 266.7 833.3 Q 200.0 833.3 200.0 766.7 L 200.0 533.3 Q 200.0 466.7 266.7 466.7 Z
`
// the shackle
const shackle = `
M 333.3 466.7 L 333.3 333.3 A 166.7 166.7 0 0 1 663.3 300.0
`


export const Unlocked = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <g>
            <path style={ico} d={body} />
            <path style={ico} d={shackle} />
        </g>
    )
}


// end of file
