// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Extent } from '~/widgets'
// locals
import styles from './styles'


// a widget that can act as a header or a title
export const Mosaic = ({ raster, tile, style }) => {
    // mix my paint
    const boxStyle = { ...styles.box, ...style.box }
    const mosaicStyle = { ...styles.mosaic, ...style.mosaic }
    const tileStyle = { ...styles.tile, ...style.tile }

    // paint me
    return (
        <div style={boxStyle} >
            <div style={mosaicStyle} >
            </div>
        </div>
    )
}


// end of file
