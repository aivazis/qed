// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


const arc = `
   M 200 500 A 300 300 0 1 1 500 800
`

const arrow = `
   M 200 600 l 150 -150 l -300 0 Z
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
            <circle style={dec} cx="500" cy="500" r="75" />
        </g>
    )
}


// end of file
