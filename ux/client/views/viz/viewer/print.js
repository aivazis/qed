// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Camera as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useGetTileURI } from '../viz/useGetTileURI'
import { useGetView } from '../viz/useGetView'
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
import { useViewports } from '../viz/useViewports'
// styles
import styles from './styles'


// control viewport synchronization with a shared camera
export const Print = ({ viewport }) => {
    // make a ref for the download link
    const link = React.useRef()

    // get the pile of registered {viewports}; mine is at {viewport}
    const { viewports } = useViewports()
    // get my view and extract my dataset
    const { dataset } = useGetView(viewport)
    // get my zoom level
    const zoom = Math.trunc(useGetZoomLevel(viewport))
    // get uri to the tile api
    const uri = useGetTileURI({ viewport })

    // i actually need the shape of the raster
    const { shape } = dataset
    // convert the zoom level into a scale
    const scale = 2 ** zoom
    // compute the dimensions of the mosaic
    const zoomedShape = shape.map(extent => Math.trunc(extent / scale))

    // make my handler
    const print = () => {
        // get viewer placemat
        const placemat = viewports[viewport]
        // measure it
        const box = placemat.getBoundingClientRect()

        // get the current scroll position
        const left = Math.trunc(placemat.scrollLeft)
        const top = Math.trunc(placemat.scrollTop)
        // clip the extents to the raster shape
        const width = Math.trunc(Math.min(box.width, zoomedShape[1] - left))
        const height = Math.trunc(Math.min(box.height, zoomedShape[0] - top))

        // form the tile
        const tile = `${top}x${left}+${height}x${width}`
        // fold the tile api
        const href = [uri, tile].join("/")
        // attach it to the link
        link.current.href = href
        // let event bubbling do the rest
        return
    }

    // my event handlers
    const behaviors = {
        // print the active view
        onClick: print,
    }

    // set my state
    const state = "enabled"
    // mix my paint
    const paint = styles.print
    // render
    return (
        <a ref={link} download href={`${uri}/0x0+512x512`} >
            <Badge size={16} state={state} behaviors={behaviors} style={paint} >
                <Shape />
            </Badge>
        </a>
    )
}


// end of file