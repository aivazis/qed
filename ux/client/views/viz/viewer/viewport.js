// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Mosaic } from '~/widgets'
// colors
import { theme } from "~/palette"
// hooks
import { useViewports, useCenterViewport } from '~/views/viz'

// locals
import { tileURI } from '.'
// components
import { Measure } from '../measure'


// export the data viewport
export const Viewport = ({ viewport, view, registrar, ...rest }) => {
    // unpack the view
    const {
        session, reader, dataset, channel, measure, zoom
    } = useFragment(viewportViewerGetViewFragment, view)
    // get the pile of registered {viewports}; i'm at {viewport}
    const { activeViewport, viewports } = useViewports()
    // make a handler that centers my viewport
    const centerViewport = useCenterViewport(viewport)
    // get the base URI for tiles
    const uri = tileURI({ reader, dataset, channel, zoom, viewport })
    // unpack what i need from the dataset
    const { shape, origin, tile } = dataset
    // convert the zoom level into a scale
    const scale = [2 ** -zoom.vertical, 2 ** -zoom.horizontal]
    // compute the dimensions of the mosaic
    const zoomedShape = shape.map((extent, idx) => Math.trunc(extent / scale[idx]))
    // center the viewport at the cursor position
    const center = ({ clientX, clientY }) => {
        // get my placemat
        const placemat = viewports[viewport]
        // measure it
        // N.B.: don't be tempted to spread the return; MDN claims it doesn't work...
        // get the viewport bounding box
        const box = placemat.getBoundingClientRect()

        // compute the location of the click relative to the viewport
        const clickX = clientX - box.left
        const clickY = clientY - box.top
        // get the current scroll position
        const left = placemat.scrollLeft
        const top = placemat.scrollTop
        // compute the new center location
        const x = left + clickX
        const y = top + clickY
        // and center there
        centerViewport({ x, y })

        // all done
        return
    }

    // assemble my controllers
    const controllers = {
        // centering at a given location
        onDoubleClick: center,
    }

    // compute my state
    const active = activeViewport === viewport

    // and render; don't forget to use the zoomed raster shape
    return (
        <Box ref={registrar} $state={active} {...controllers} {...rest} >
            {/* the data tiles */}
            <View uri={uri}
                origin={origin} shape={shape} tile={tile}
                zoom={[zoom.vertical, zoom.horizontal]}
                session={session} />
            {/* the measure layer */}
            {measure.active &&
                <Measure viewport={viewport} view={view} shape={zoomedShape} scale={scale} />
            }
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
    border: 1px solid ${props => props.$state ? theme.page.viewportBorder : theme.page.active};
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
const canSkipRender = (prev, next) => {
    // if the {session} has changed
    if (prev.session != next.session) {
        // render
        return false
    }
    // if the {zoom} level has changed
    if (prev.zoom[0] != next.zoom[0] || prev.zoom[1] != next.zoom[1]) {
        // render
        return false
    }
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
const View = React.memo(DataTiles, canSkipRender)


// my fragment
const viewportViewerGetViewFragment = graphql`
    fragment viewportViewerGetViewFragment on View {
        id
        session
        reader {
            id
            name
            uri
            api
        }
        dataset {
            name
            shape
            origin
            tile
        }
        channel {
            tag
        }
        measure {
            active
        }
        zoom {
            horizontal
            vertical
        }
    }
`


// end of file
