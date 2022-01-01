// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the eye lid
const eyelid = `
M 100 500
C 350 150 650 150 900 500
C 650 850 350 850 100 500
Z
`

// render the shape
export const Eye = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const deco = { ...styles.decoration, ...style?.decoration }

    // paint me
    return (
        <>
            <path style={ico} d={eyelid} />
            <circle style={deco}
                cx="500" cy="500" r="125" />
        </>
    )
}


// end of file
