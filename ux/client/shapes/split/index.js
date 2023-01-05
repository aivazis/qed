// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the eye lid
const split = `
M 100 100 L 100 900 L 900 900 L 900 100 Z
M 500 100 L 500 900
`

// render the shape
export const Split = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <path style={ico} d={split} />
    )
}


// end of file
