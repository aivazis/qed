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
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
import { useViewports } from '../viz/useViewports'
import { useMeasureLayer } from '../viewer/useMeasureLayer'
// components
import { Measure } from '../measure'
// styles
import styles from './styles'


// export the data viewport
export const Viewport = ({ viewport, view, uri, registrar, ...rest }) => {
    // get the state of the measuring layer
    const measure = useMeasureLayer()
    // get my zoom
    const zoom = Math.trunc(useGetZoomLevel(viewport))
    // get the pile of registered {viewports}; i'm at {viewport}
    const viewports = useViewports()

    // get my view info
    const { dataset } = view
    // and unpack what i need
    const { shape, origin, tile } = dataset

    // convert the zoom level into a scale
    const scale = 2 ** zoom

    // compute the dimensions of the mosaic
    const width = Math.trunc(shape[1] / scale)
    const height = Math.trunc(shape[0] / scale)
    // assemble in a single object
    const raster = { height, width }
    // and fold my zoom level into the data request uri
    const withZoom = [uri, zoom].join("/")

    // center the viewport at the cursor position
    const center = ({ clientX, clientY }) => {
        // get my placemat
        const placemat = viewports[viewport]
        // measure it
        // N.B.: don't be tempted to spread the return; MDN claims it doesn't work...
        // get the viewport bounding box
        const box = placemat.getBoundingClientRect()

        // compute the location of the click relative to the viewport
        const x = clientX - box.left
        const y = clientY - box.top
        // get the size of the viewport
        const width = box.width
        const height = box.height
        // get the current scroll position
        const left = placemat.scrollLeft
        const top = placemat.scrollTop
        // compute the new location
        const newX = left + x - width / 2
        const newY = top + y - height / 2
        // and scroll to the new location
        placemat.scroll({ left: newX, top: newY, behavior: "smooth" })

        // all done
        return
    }

    // assemble my controllers
    const controllers = {
        // centering at a given location
        onDoubleClick: center,
    }

    // mix my paint
    const paint = styles.viewport({ width, height })
    // and render; don't forget to use the zoomed raster shape
    return (
        <div ref={registrar} style={paint.box} {...controllers} {...rest} >
            <Mosaic uri={withZoom}
                raster={[height, width]} origin={origin} tile={tile}
                style={paint}
            />
            {measure && <Measure shape={shape} raster={raster} zoom={zoom} />}
        </div>
    )
}


// end of file
