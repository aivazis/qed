// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'

// render the shape
export const Factory = ({ highlight, cell = 1, style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const deco = { ...styles.decoration, ...style?.decoration }
    const conn = { ...styles.connector, ...style?.connector }

    // paint me; don't forget we are using a quarter cell grid,
    // i.e.a diagram cell is four grid cells
    return (
        <>
            <line style={conn} x1={-cell} y1="0" x2={cell} y2="0" />
            <line style={conn} x1="0" y1="0" x2="0" y2="-2" />
            <path style={ico} d="M -0.125 0 L 0 0.125 L 0.125 0 L 0 -0.125 Z" />
            <circle style={ico} cx="0" cy="-1.5" r=".5" />
            {highlight ? <circle cx="0" cy="-1.5" r=".75" style={deco} /> : null}
        </>
    )
}


// end of file
