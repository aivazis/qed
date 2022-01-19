// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a container with author and copyright notes
export const Toolbar = ({ direction, style, children }) => {
    // mix my paint
    const paint = styles.toolbar({ client: style, direction })
    // and render
    return (
        <nav style={paint} >
            {children}
        </nav>
    )
}


// end of file
