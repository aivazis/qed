// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Spacer } from '~/widgets'

// locals
import styles from './styles'


// a widget that can act as a header or a title
export const Header = ({ title, children, style }) => {
    // mix my styles
    const headerStyle = { ...styles, ...style }

    // paint me
    return (
        <div style={headerStyle} >
            {title}
            <Spacer />
            {children}
        </div>
    )
}


// end of file
