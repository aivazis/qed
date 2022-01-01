// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a stylable shimmy
const spacer = ({ style }) => {
    // mix my styles
    const spacerStyle = { ...styles, ...style }

    // paint me
    return (
        <div style={spacerStyle} />
    )
}


// publish
export default spacer


// end of file
