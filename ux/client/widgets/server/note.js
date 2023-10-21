// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// styles
import styles from './styles'


export const Note = ({ style }) => {
    // mix my paint
    const paint = { ...style.box, ...styles.box, ...style.text, ...styles.text }
    // render
    return (
        <div style={paint}>
            contacting the server...
        </div>
    )
}


// end of file
