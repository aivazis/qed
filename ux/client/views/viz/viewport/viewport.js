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
import { useViewports } from '../viz/useViewports'
import { usePanViewportCamera } from './usePanViewportCamera'
import { useGetViewportCameraZoom } from './useGetViewportCameraZoom'
import { useGetViewportCameraPostion } from './useGetViewportCameraPosition'
// styles
import styles from './styles'


// export the data viewport
const Panel = ({ viewport, view, uri, registrar, ...rest }) => {
    // get the pile of registered {viewports}; i'm at {viewport}
    const viewports = useViewports()
    // get the viewport camera position
    const camera = useGetViewportCameraPostion()
    // get the current zoom level
    const zoom = useGetViewportCameraZoom()
    // and its panning controller
    const panViewportCamera = usePanViewportCamera()

    // get my view info
    const { dataset } = view
    // and unpack what i need
    const { shape, origin, tile } = dataset

    // compute the dimensions of the mosaic
    const width = Math.trunc(shape[1] / zoom)
    const height = Math.trunc(shape[0] / zoom)
    // and fold my zoom level into the data request uri
    const withZoom = [uri, zoom].join("/")

    // build my scroll handler
    const scroll = evt => {
        // get the scrolling element
        const element = evt.target
        // get the scroll coordinates
        const y = Math.max(element.scrollTop, 0)
        const x = Math.max(element.scrollLeft, 0)
        // update the viewport camera
        panViewportCamera({ x, y })
        // done
        return
    }
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

        // get the current camera position and shift it
        const newAt = { ...camera.current, x: newX, y: newY }
        // and update
        panViewportCamera(newAt)

        // all done
        return
    }
    // assemble my controllers
    const controllers = {
        // panning the viewport camera
        onScroll: scroll,
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
        </div>
    )
}


// context
import { Provider } from './context'
// turn the panel into a context provider and publish
export const Viewport = props => (
    <Provider>
        <Panel {...props} />
    </Provider>
)


// end of file
