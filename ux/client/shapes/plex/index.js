// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'

// render the shape
export const Plex = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <rect style={ico} x="-0.125" y="-0.125" width="0.25" height="0.25" />
    )
}


// end of file
