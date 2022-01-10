// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Mosaic } from '~/widgets'

// locals
// hooks
import { useRegisterViewport } from './useRegisterViewport'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewport = React.forwardRef(({ view, uri }, ref) => {
    // get my view info
    const { dataset } = view
    // and unpack what i need
    const { shape, tile } = dataset

    // mix my paint
    // for the viewport
    const viewportStyle = styles.viewport
    // and the mosaic
    const mosaicStyle = {
        // for the data viewport
        mosaic: {
            // base
            ...styles.viewport.mosaic,
            // resize to the dataset shape
            width: `${shape[1]}px`,
            height: `${shape[0]}px`,
        },
    }

    // render
    return (
        < div ref={ref} style={viewportStyle.box} >
            <Mosaic uri={uri} raster={shape} tile={tile} style={mosaicStyle} />
        </div >
    )
})


// end of file