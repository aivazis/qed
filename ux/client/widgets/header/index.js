// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a widget that can act as a header or a title
export const Header = ({ title, style }) => {
    // mix my styles
    const headerStyle = { ...styles, ...style }

    // paint me
    return (
        <div style={headerStyle} >
            {title}
        </div>
    )
}


// end of file
