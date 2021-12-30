// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the eye lid
const locked = `
M 150 500 L 150 900 L 850 900 L 850 500 Z
M 250 500 A 250 400 0 0 1 750 500
`

// render the shape
export const Locked = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <path style={ico} d={locked} />
    )
}


// end of file
