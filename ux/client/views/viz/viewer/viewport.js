// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


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
    const scale = { vertical: 2 ** -zoom.vertical, horizontal: 2 ** -zoom.horizontal }
    // compute the dimensions of the mosaic
    const zoomedShape = { width: shape[1] / scale.horizontal, height: shape[0] / scale.vertical }

    // the scroll position lives in *rendered* pixels, which grow as 2**zoom; when the zoom level
    // changes in place, the mosaic resizes but the browser leaves the old scroll offset alone, so
    // it no longer points at the same source pixel -- and if it now exceeds the smaller mosaic, it
    // gets clamped to a corner. we rescale the offset by the change in zoom factor (below), holding
    // the source pixel under the viewport center fixed, so changing zoom keeps you looking at the
    // same place. but the resize clamps the offset in the same commit, *before* a layout effect
    // could read it, so we cannot trust the post-resize value; track the live offset here, while it
    // is still valid for the current zoom, and rescale that
    const lastScroll = React.useRef({ left: 0, top: 0 })
    React.useEffect(() => {
        // get my scrolling container
        const placemat = viewports[viewport]
        // if there is none yet, there is nothing to track
        if (!placemat) {
            // bail
            return
        }
        // record the offset whenever it changes, so we always have its pre-resize value on hand
        const track = () => {
            // stash the live offset
            lastScroll.current = { left: placemat.scrollLeft, top: placemat.scrollTop }
            // all done
            return
        }
        // seed it, then follow along
        track()
        placemat.addEventListener("scroll", track)
        // clean up
        return () => placemat.removeEventListener("scroll", track)
    }, [viewport, viewports])

    // rescale the tracked offset when the zoom level changes, holding the centered source pixel put
    const previousZoom = React.useRef(zoom)
    React.useLayoutEffect(() => {
        // get my scrolling container
        const placemat = viewports[viewport]
        // the previous zoom levels
        const previous = previousZoom.current
        // remember the current ones for next time
        previousZoom.current = zoom
        // the per-axis change in the rendered-pixel scale
        const ratioX = 2 ** (zoom.horizontal - previous.horizontal)
        const ratioY = 2 ** (zoom.vertical - previous.vertical)
        // if there is no container yet, or the zoom did not actually change, there is nothing to do
        if (!placemat || (ratioX === 1 && ratioY === 1)) {
            // bail
            return
        }
        // measure the viewport
        const box = placemat.getBoundingClientRect()
        // use the offset as it was *before* this commit resized (and clamped) the mosaic
        const { left, top } = lastScroll.current
        // rescale each offset about the viewport center, so the centered source pixel stays put
        placemat.scrollLeft = (left + box.width / 2) * ratioX - box.width / 2
        placemat.scrollTop = (top + box.height / 2) * ratioY - box.height / 2
        // all done
        return
    }, [viewport, viewports, zoom.horizontal, zoom.vertical])
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
        <Box ref={registrar} $state={active} {...controllers} {...rest}
            data-qed-region="viewport"
            data-qed-shape={shape.join(",")}
            data-qed-zoom={[zoom.vertical, zoom.horizontal].join(",")} >
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
// N.B.: do NOT set width/height here. {Mosaic} sizes its own {Box} from the *zoomed* shape; this
// wrapper's class is now forwarded onto that same {Box} (the mosaic spreads {...rest}), so a
// width/height here -- computed from the *raw* shape -- would override the zoomed size and freeze
// the scroll extent at zoom 0. let {Mosaic} own its geometry.
const DataTiles = styled(Mosaic)`
    background-color: hsl(0deg, 5%, 7%);
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
