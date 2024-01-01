// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a container with author and copyright notes
export const Toolbar = ({ direction, style, children }) => {
    // mix my styles
    const boxStyle = { ...styles.box, ...style?.box, flexDirection: direction }

    // paint me
    return (
        <nav style={boxStyle} >
            {children}
        </nav>
    )
}


// end of file
