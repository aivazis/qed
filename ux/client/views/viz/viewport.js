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
import { useViews } from './useViews'
import { useRegisterViewport } from './useRegisterViewport'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewport = ({ view }) => {
    // get the list of views
    const { views } = useViews()
    // register my viewport
    const viewport = useRegisterViewport()

    // get my view info
    const { dataset } = views[view]
    // and unpack what i need
    const { shape, tile } = dataset

    // mix my paint
    const viewportStyle = {
        // for the overall box
        box: {
            // base
            ...styles.viewport.box,
        },
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
        < div ref={viewport} style={viewportStyle.box} >
            < Mosaic raster={shape} tile={tile} style={viewportStyle} />
        </div >
    )
}


// end of file