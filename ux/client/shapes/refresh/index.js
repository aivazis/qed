// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


const arc = `
   M 100 500 A 400 400 0 1 1 500 900
`

const arrow = `
   M 100 575 l 100 -100 l -200 0 Z
`

// render the shape
export const Refresh = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const dec = { ...styles.decoration, ...style?.decoration }

    // paint me
    return (
        <g>
            <path style={ico} d={arc} />
            <path style={dec} d={arrow} />
            <circle style={dec} cx="500" cy="500" r="100" />
        </g>
    )
}


// end of file
