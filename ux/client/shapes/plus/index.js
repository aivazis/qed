// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the eye lid
const x = `
M 0 500 l 1000 0
M 500 0 l 0 1000
`

// render the shape
export const Plus = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <path style={ico} d={x} />
    )
}


// end of file
