// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the shape
export const Square = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <rect style={ico} x={50} y={50} width={900} height={900} />
    )
}


// end of file
