// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shapes
import { Camera as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'
// hooks
import { useViewports } from '~/views/viz'

// locals
// the tile URI factory
import { tileURI } from '.'
// styles
import styles from './styles'


// control viewport synchronization with a shared camera
export const Print = ({ viewport, view }) => {
    // extract my fragment from {view}
    const { reader, dataset, channel, zoom } = useFragment(printViewerGetViewFragment, view)
    // make a ref for the download link
    const link = React.useRef()
    // get the pile of registered {viewports}; mine is at {viewport}
    const { viewports } = useViewports()
    // get uri to the tile api
    const uri = tileURI({ reader, dataset, channel, zoom })
    // convert the zoom level into a scale
    const scale = [zoom.vertical, zoom.horizontal].map(level => 2 ** -level)
    // get the shape of the raster
    const { shape } = dataset
    // compute the dimensions of the mosaic
    const zoomedShape = shape.map((extent, idx) => extent / scale[idx])
    // make my handler
    const print = evt => {
        // get the state of the alt key
        const { altKey } = evt
        // get viewer placemat
        const placemat = viewports[viewport]
        // measure it
        const box = placemat.getBoundingClientRect()

        // get the current scroll position
        const left = altKey ? 0 : Math.trunc(placemat.scrollLeft)
        const top = altKey ? 0 : Math.trunc(placemat.scrollTop)
        // clip the extents to the raster shape
        const width = Math.trunc(
            altKey ? zoomedShape[1] : Math.min(box.width, zoomedShape[1] - left)
        )
        const height = Math.trunc(
            altKey ? zoomedShape[0] : Math.min(box.height, zoomedShape[0] - top)
        )

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


// my fragment
const printViewerGetViewFragment = graphql`
    fragment printViewerGetViewFragment on View {
        reader {
            api
        }
        dataset {
            name
            shape
        }
        channel {
            tag
        }
        zoom {
            horizontal
            vertical
        }
    }
`


// end of file