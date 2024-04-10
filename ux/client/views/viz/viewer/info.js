// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// widgets
import { Meta } from '~/widgets'
// hooks
import { useViewports } from '~/views/viz'

// locals
import { tileURI } from '.'
// styles
import styles from './styles'


// export the data viewer
export const Info = ({ viewport, view }) => {
    // unpack the view
    const { reader, dataset, channel, zoom } = useFragment(infoViewerGetViewFragment, view)
    // get the viewport registry
    const { viewports } = useViewports()
    // make room for the cursor position
    const [location, setLocation] = React.useState({ x: 0, y: 0 })

    // assemble the data request URI
    const base = tileURI({ reader, dataset, channel, zoom, viewport })
    // extract the relevant metadata
    const { name: readerName, id, uri } = reader
    const { name: datasetName, datatype, shape, origin, tile } = dataset
    // unpack the zoom level
    const level = [zoom.vertical, zoom.horizontal]
    // convert it into a scale
    const scale = level.map(value => 2 ** -value)
    // project the location to image coordinates
    const pixel = {
        x: Math.trunc(location.x * scale[1]),
        y: Math.trunc(location.y * scale[0])
    }
    // scale the shape to the current zoom level
    const effectiveShape = shape.map((s, idx) => s / scale[idx])
    // build the handler of the mouse movement
    const track = evt => {
        // get the viewport, not whatever the mouse is over
        const element = evt.currentTarget
        // measure it
        const box = element.getBoundingClientRect()
        // compute the location of the mouse relative to the viewport
        // and take the zoom level into account
        const x = Math.trunc(element.scrollLeft + evt.clientX - box.left)
        const y = Math.trunc(element.scrollTop + evt.clientY - box.top)
        // if the position overflows the dataset along the x-axis
        if (x < 0 || x > effectiveShape[1]) {
            // bail
            return
        }
        // repeat for the y axis
        if (y < 0 || y > effectiveShape[0]) {
            // bail
            return
        }
        // record the current mouse location; this triggers the {sample} query to refresh
        setLocation({ x, y })
        // all done
        return
    }

    // install a tracker on the active viewport
    React.useEffect(() => {
        // get the active viewport ref
        const target = viewports[viewport]
        // install the tracker
        target?.addEventListener("mousemove", track)
        // make an abort controller
        const controller = new AbortController()
        // and register a clean up
        return () => {
            // that removes the listeners
            target?.removeEventListener("mousemove", track)
            // and aborts any pending requests
            controller.abort()
            // all done
            return
        }
    })

    // mix my paint
    const paint = styles.viewer
    // and render
    return (
        < Meta.Table min={0} initial={1} max={5} style={paint} >
            <Meta.Entry threshold={1} attribute="pixel" style={paint}>
                {`(${pixel.y}, ${pixel.x})`}
            </Meta.Entry>
            <Meta.Entry threshold={1} attribute="cursor" style={paint}>
                {`(${location.y}, ${location.x})`}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="uri" style={paint}>
                {uri}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="shape" style={paint}>
                {shape.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="zoom level" style={paint}>
                {level.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="effective shape" style={paint}>
                {effectiveShape.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="tile" style={paint}>
                {tile.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="origin" style={paint}>
                {origin.join(", ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="reader" style={paint}>
                {id}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="type" style={paint}>
                {datatype}
            </Meta.Entry>
            <Meta.Entry threshold={4} attribute="reader" style={paint}>
                {readerName}
            </Meta.Entry>
            <Meta.Entry threshold={4} attribute="dataset" style={paint}>
                {datasetName}
            </Meta.Entry>
            <Meta.Entry threshold={5} attribute="data" style={paint}>
                {base}
            </Meta.Entry>
        </Meta.Table>
    )
}


// my fragment
const infoViewerGetViewFragment = graphql`
    fragment infoViewerGetViewFragment on View {
        reader {
            id
            name
            uri
            api
        }
        dataset {
            name
            datatype
            shape
            origin
            tile
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
