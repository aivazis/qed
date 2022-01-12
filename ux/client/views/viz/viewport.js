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
import { usePanViewportCamera } from './usePanViewportCamera'
import { useGetViewportCameraPostion } from './useGetViewportCameraPosition'
// styles
import styles from './styles'


// display the datasets associated with this reader
const Panel = React.forwardRef(({ view, uri, ...rest }, ref) => {
    // get my camera position
    const { z } = useGetViewportCameraPostion()
    // and its panning controller
    const panViewportCamera = usePanViewportCamera(ref)

    // get my view info
    const { dataset } = view
    // and unpack what i need
    const { shape, tile } = dataset

    // compute the dimensions of the mosaic
    const width = Math.trunc(shape[1] / z)
    const height = Math.trunc(shape[0] / z)
    // and fold my zoom level into the data request uri
    const withZoom = [uri, z].join("/")

    // build my scroll handler
    const pan = (evt) => {
        // get the scrolling element
        const element = evt.target
        // get the scroll coordinates
        const y = Math.max(element.scrollTop, 0)
        const x = Math.max(element.scrollLeft, 0)
        // update the shared camera
        panViewportCamera({ x, y })
        // done
        return
    }

    // mix my paint
    // for the viewport
    const viewportStyle = styles.viewport
    // and the mosaic
    const mosaicStyle = {
        // for the data viewport
        mosaic: {
            // base
            ...styles.viewport.mosaic,
            // resize to the dataset shape, taking the zoom factor into account
            width: `${width}px`,
            height: `${height}px`,
        },
    }

    // render; don't forget to use the zoomed raster shape
    return (
        <div ref={ref} style={viewportStyle.box} onScroll={pan} {...rest} >
            <Mosaic uri={withZoom} raster={[height, width]} tile={tile} style={mosaicStyle} />
        </div>
    )
})


// context
import { ViewportProvider } from './viewportContext'
// turn the panel into a context provider and publish
export const Viewport = React.forwardRef((props, ref) => {
    // set up the context provider
    return (
        <ViewportProvider>
            <Panel ref={ref} {...props} />
        </ViewportProvider>
    )
})


// end of file
