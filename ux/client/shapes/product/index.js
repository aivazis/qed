// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the shape
export const Product = ({ highlight, style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const deco = { ...styles.decoration, ...style?.decoration }

    // paint me; don't forget we are using a quarter cell grid,
    // i.e.a diagram cell is four grid cells
    return (
        <>
            <circle cx="0" cy="0" r=".5" style={ico} />
            {highlight ? <circle cx="0" cy="0" r=".75" style={deco} /> : null}
        </>
    )
}


// end of file
