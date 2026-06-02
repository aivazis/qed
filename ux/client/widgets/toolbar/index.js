// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a strip of controls; defaults to a navigation landmark, but the client may override
// {role} (e.g. "toolbar") and supply an {aria-label} through {rest}
export const Toolbar = ({ direction, style, children, ...rest }) => {
    // mix my styles
    const boxStyle = { ...styles.box, ...style?.box, flexDirection: direction }

    // paint me
    return (
        <nav style={boxStyle} data-pyre-widget="toolbar" {...rest} >
            {children}
        </nav>
    )
}


// end of file
