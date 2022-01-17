// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// styles
import styles from './styles'


// setup a container for displaying metadata
export const Table = ({ style, children, ...rest }) => {
    // mix my pain
    const tableStyle = { ...styles.box, ...style?.box }

    // render
    return (
        <table style={tableStyle} {...rest}>
            <tbody>
                {children}
            </tbody>
        </table >
    )
}


// end of file