// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the path data
const chevron = `M 375 125 L 750 500 L 375 875`


// render the shape
export const Chevron = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <path style={ico} d={chevron} />
    )
}


// end of file
