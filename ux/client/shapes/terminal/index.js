// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'

// render the shape
export const Terminal = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const deco = { ...styles.decoration, ...style?.decoration }

    // paint me
    return (
        <>
            <circle style={deco} cx="0" cy="0" r="0.5" />
            <path style={ico} d="M -0.20 -0.20 L 0.20 0.20 M -0.20 0.20 L 0.20 -0.20" />
        </>
    )
}


// end of file
