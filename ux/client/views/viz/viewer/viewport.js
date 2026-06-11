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
// hooks
import { useLookAt } from './useLookAt'
// components
import { Measure } from '../measure'


// how close two look-at centers must be, in source pixels, to count as the same place; this absorbs
// float noise and the sub-pixel drift of the zoom rescale, so a programmatic scroll does not echo
const EPSILON = 0.5

// the source pixel under the center of {placemat}, derived from its rendered zoom and size; the
// inverse of {lookAtCenter}, and the same mapping {window.qed.centerOn} and the minimap use
const centerOf = placemat => {
    // read the rendered zoom off the markup, as "vertical,horizontal"
    const [vertical, horizontal] = placemat.getAttribute("data-qed-zoom").split(",").map(Number)
    // scroll offsets are in rendered pixels, which grow as 2**zoom; convert the center to source
    return {
        row: (placemat.scrollTop + placemat.clientHeight / 2) * 2 ** -vertical,
        col: (placemat.scrollLeft + placemat.clientWidth / 2) * 2 ** -horizontal,
    }
}

// scroll {placemat} so the source pixel {row, col} sits at the center of the visible window
const lookAtCenter = (placemat, { row, col }) => {
    // read the rendered zoom off the markup, as "vertical,horizontal"
    const [vertical, horizontal] = placemat.getAttribute("data-qed-zoom").split(",").map(Number)
    // convert source pixels to rendered ones and place the target at the center
    placemat.scrollLeft = col * 2 ** horizontal - placemat.clientWidth / 2
    placemat.scrollTop = row * 2 ** vertical - placemat.clientHeight / 2
}

// whether two look-at centers point at the same source pixel, within {EPSILON}
const same = (a, b) =>
    a != null && b != null && Math.abs(a.row - b.row) < EPSILON && Math.abs(a.col - b.col) < EPSILON

// ask lazysizes to load whatever is now visible. it defers loads during a fast scroll and keys off
// its own scroll detection; when we move the view -- the originator coming to rest, or a peer being
// recentered from the server -- that detection can be outrun, leaving freshly-revealed tiles blank.
// nudging it once the view is settled loads them without waiting for another scroll
const loadVisibleTiles = () => window.lazySizes?.loader?.checkElems?.()


// export the data viewport
export const Viewport = ({ viewport, view, registrar, ...rest }) => {
    // unpack the view
    const {
        session, reader, dataset, channel, measure, zoom, center: serverCenter
    } = useFragment(viewportViewerGetViewFragment, view)
    // get the pile of registered {viewports}; i'm at {viewport}
    const { activeViewport, viewports } = useViewports()
    // make a handler that centers my viewport
    const centerViewport = useCenterViewport(viewport)
    // a handler that pushes my look-at center to the server, so my scroll syncs to every client
    const { set: lookAt } = useLookAt(viewport)
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
    // the look-at center we last sent to, or adopted from, the server; a scroll that lands here is an
    // echo of our own push or of a programmatic scroll, and must not bounce back out to the server
    const lastCenter = React.useRef(null)
    // raised while the user is actively scrolling, so a server echo cannot yank the view mid-gesture;
    // a scroll has no clean "pointer up", so we lower it on a short idle timer instead
    const interacting = React.useRef(false)
    // the latest center seen while scrolling, flushed to the server only once the scroll settles
    const pendingCenter = React.useRef(null)
    const settleTimer = React.useRef(null)
    // {lookAt} is a fresh closure each render; keep it in a ref so the scroll listener stays stable
    const lookAtRef = React.useRef(lookAt)
    React.useEffect(() => { lookAtRef.current = lookAt })
    React.useEffect(() => {
        // get my scrolling container
        const placemat = viewports[viewport]
        // if there is none yet, there is nothing to track
        if (!placemat) {
            // bail
            return
        }
        // every scroll event fires a mutation, and every mutation triggers a full-state refetch on
        // every client over live sync; pushing on each tick of a drag would be a refetch storm that
        // re-renders the viewport faster than its tiles can lazy-load. so we track the position live
        // but flush only the FINAL center, once the scroll has been still for a beat -- the look-at
        // sync cares where you land, not the path you took to get there
        const flush = () => {
            // the scroll has settled
            interacting.current = false
            // the place we came to rest
            const center = pendingCenter.current
            pendingCenter.current = null
            // push the final center, unless there is nothing pending or it is where we already are
            if (center != null && !same(center, lastCenter.current)) {
                // remember it as ours and push it
                lastCenter.current = center
                lookAtRef.current(center)
            }
            // the view has come to rest; load whatever scrolled into view but lazysizes deferred
            loadVisibleTiles()
            // all done
            return
        }
        const track = () => {
            // stash the live offset, so the zoom rescale below has its pre-resize value
            lastScroll.current = { left: placemat.scrollLeft, top: placemat.scrollTop }
            // where am i looking now, in source pixels?
            const here = centerOf(placemat)
            // the first observation is just a baseline; adopt it silently and never push it
            if (lastCenter.current == null) {
                lastCenter.current = here
                return
            }
            // a programmatic scroll (the reconcile effect or the zoom rescale) lands on the
            // remembered center; recognize it as an echo and leave the server alone
            if (same(here, lastCenter.current)) {
                return
            }
            // a real move: hold off server echoes, remember the latest spot, and (re)arm the flush
            // so the push lands only after the scroll goes quiet
            interacting.current = true
            pendingCenter.current = here
            if (settleTimer.current) {
                clearTimeout(settleTimer.current)
            }
            settleTimer.current = setTimeout(flush, 150)
            // all done
            return
        }
        // seed it, then follow along; passive, so we never delay the scroll or starve lazysizes
        track()
        placemat.addEventListener("scroll", track, { passive: true })
        // clean up; drop any pending flush so it cannot fire after unmount
        return () => {
            placemat.removeEventListener("scroll", track)
            if (settleTimer.current) {
                clearTimeout(settleTimer.current)
            }
        }
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
        // the rescale holds the look-at center fixed; record where we actually landed (the offset may
        // clamp at an edge) so the scroll event it triggers is recognized as an echo, not pushed out
        lastCenter.current = centerOf(placemat)
        // all done
        return
    }, [viewport, viewports, zoom.horizontal, zoom.vertical])

    // adopt a look-at center pushed from the server -- a peer panned, or this is our first sync on
    // load. skip while the user is actively scrolling so we never fight the pointer
    React.useEffect(() => {
        // get my scrolling container
        const placemat = viewports[viewport]
        // if there is none yet, or i have none to adopt, or the user is mid-gesture, leave it be
        if (!placemat || !serverCenter || interacting.current) {
            // bail
            return
        }
        // the center the server wants me to look at
        const target = { row: serverCenter.row, col: serverCenter.col }
        // if it already matches where i am looking, there is nothing to do
        if (same(target, lastCenter.current)) {
            // bail
            return
        }
        // scroll there
        lookAtCenter(placemat, target)
        // record where i actually landed (the scroll may clamp at an edge) so the scroll event this
        // triggers is recognized as an echo rather than pushed back to the server
        lastCenter.current = centerOf(placemat)
        // load whatever this recenter brought into view
        loadVisibleTiles()
        // all done
        return
    }, [viewport, viewports, serverCenter?.row, serverCenter?.col])
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
        center {
            row
            col
        }
    }
`


// end of file
