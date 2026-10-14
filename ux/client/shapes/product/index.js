// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the shape; an {empty} product, a slot whose instance holds nothing, is struck through
export const Product = ({ highlight, empty, style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const deco = { ...styles.decoration, ...style?.decoration }

    // paint me; don't forget we are using a quarter cell grid,
    // i.e.a diagram cell is four grid cells
    return (
        <>
            <circle cx="0" cy="0" r=".5" style={ico} data-qed-grip />
            {empty ? <line x1="-.35" y1=".35" x2=".35" y2="-.35" style={styles.strike} /> : null}
            {highlight ? <circle cx="0" cy="0" r=".75" style={deco} /> : null}
        </>
    )
}


// end of file
