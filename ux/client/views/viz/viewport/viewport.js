// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Mosaic } from '~/widgets'

// locals
// hooks
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
import { useViewports } from '../viz/useViewports'
import { useMeasureLayer } from '../viz/useMeasureLayer'
// components
import { Measure } from '../measure'


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
    const zoomedShape = [height, width]
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

    // and render; don't forget to use the zoomed raster shape
    return (
        <Box ref={registrar} {...controllers} {...rest} >
            {/* the data tiles */}
            <View uri={withZoom} shape={zoomedShape} origin={origin} tile={tile} />
            {/* the measure layer */}
            {measure && <Measure shape={zoomedShape} zoom={zoom} />}
        </Box>
    )
}


// style my box
const Box = styled.div`
    position: relative;
    /* layout */
    flex: 1 1 100%;
    overflow: auto;
    min-width: 300px;
    min-height: 300px;
    margin: 0.25rem 0.5rem 0.5rem 0.5rem;
    border: 2px solid hsl(28deg, 30%, 25%);
    background-color: hsl(28deg, 30%, 5%);
`


// style {Mosaic}
const DataTiles = styled(Mosaic)`
    background-color: hsl(0deg, 5%, 7%);
    width: ${props => props.shape[1]}px;
    height: ${props => props.shape[0]}px;
`

// memoize it
// we need a function that looks at {props} and decides whether the mosaic should render
const shouldRender = (prev, next) => {
    // if the {uri} has changed
    if (prev.uri != next.uri) {
        // render
        return false
    }
    // if the raster {shape} has changed
    if (prev.shape[0] != next.shape[0] || prev.shape[1] != next.shape[1]) {
        // render
        return false
    }
    // otherwise, skip the render phase
    return true
}

// and a wrapper over the styled {Mosaic}
const View = React.memo(DataTiles, shouldRender)


// end of file
