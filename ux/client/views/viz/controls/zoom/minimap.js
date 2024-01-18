// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useViewports } from '../../viz/useViewports'
// style
import { theme } from '~/palette'


// export the minimap
export const Minimap = ({ ils, shape, zoom }) => {
    // we have
    // - the shape of the dataset in the active view
    // - the current zoom level
    // we need
    // - the origin + shape of the active viewport

    // make a ref for the placemat
    const placemat = React.useRef(null)
    // and one for the viewport rep
    const rep = React.useRef(null)
    // the dragging flag, used for dragging the minimap rendering of the viewport
    const [dragging, setDragging] = React.useState(null)
    // and a place to park position information to support the dragging calculations
    const cursor = React.useRef(null)

    // storage for the origin of the viewport
    const [origin, setOrigin] = React.useState({ x: 0, y: 0 })
    // and its size
    const [extent, setExtent] = React.useState({ width: 0, height: 0 })
    // get the viewport information
    const { activeViewport, viewports } = useViewports()

    // unpack the dataset shape
    const [dHeight, dWidth] = shape
    // unpack the zoom
    const [zoomX, zoomY] = [2 ** zoom, 2 ** zoom]
    // unpack the viewport origin
    const { x, y } = origin
    // and its extent
    const { width, height } = extent
    // set the scale
    const scale = 1 / Math.max(dWidth, zoomX * (x + width),
        dHeight, zoomY * (y + height))

    // install the trackers on the active viewport
    React.useEffect(() => {
        // get the active viewport ref
        const viewport = viewports[activeViewport]
        // if we don't have one
        if (!viewport) {
            // bail
            return
        }
        // get the position of the view
        const x = viewport.scrollLeft
        const y = viewport.scrollTop
        // set the origin
        setOrigin({ x, y })
        // measure it
        // N.B.: don't be tempted to spread the return; MDN claims it doesn't work...
        const box = viewport.getBoundingClientRect()
        // get the shape of the view
        const width = box.width
        const height = box.height
        // set the extent
        setExtent({ width, height })

        // build the callback for the viewport resize observer
        const resize = entries => {
            // go through the observer targets
            entries.forEach(entry => {
                // if the target element is not my viewport, for some unfathomable reason
                if (entry.target !== viewport) {
                    // bail
                    return
                }
                // initialize the extent
                let extent = { height: undefined, width: undefined }
                // if the target has a content box
                if (entry.contentBoxSize) {
                    // grab the first (and hopefully only) fragment
                    const contents = entry.contentBoxSize[0]
                    // convert it into an extent
                    extent = { width: contents.inlineSize, height: contents.blockSize }
                } else {
                    // use the legacy api
                    extent = entry.contentRect
                }
                // in any case, adjust my understanding of the viewport size
                setExtent(extent)
                // and done
                return
            })
            // all done
            return
        }
        // make a resize observer
        const observer = new window.ResizeObserver(resize)
        // register the viewport
        observer.observe(viewport)

        // now, handle viewport scrolling
        const scroll = () => {
            // deduce the scroll position
            const origin = { x: viewport.scrollLeft, y: viewport.scrollTop }
            // update the viewport origin
            setOrigin(origin)
            // all done
            return
        }
        // by registering a listener
        viewport.addEventListener("scroll", scroll)

        // event handlers for dragging the viewport rep within the minimap
        // initiate the dragging
        const startDragging = evt => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // and quash any side effect
            evt.preventDefault()
            // set the flag
            setDragging(true)
            // record the event location
            cursor.current = { x: evt.clientX, y: evt.clientY }
            // all done
            return
        }
        // terminate the dragging
        const stopDragging = evt => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // and quash any side effect
            evt.preventDefault()
            // set the flag
            setDragging(false)
            // record the event location
            cursor.current = { x: evt.clientX, y: evt.clientY }
            // all done
            return
        }

        // attach the mouse down handler to the viewport rep
        rep.current.addEventListener("mousedown", startDragging)
        // and the rest to the placemat
        placemat.current.addEventListener("mouseup", stopDragging)
        placemat.current.addEventListener("mouseleave", stopDragging)

        // register a clean up
        return () => {
            // if we have a valid viewport
            if (viewport) {
                // disconnect it from the observer
                observer.disconnect()
                // remove the scroll listener
                viewport.removeEventListener("scroll", scroll)
            }
            // if the viewport rep is still around
            if (rep.current) {
                // remove its event listeners
                rep.current.removeEventListener("mousedown", startDragging)
            }
            // if the placemat is still around
            if (placemat.current) {
                // remove its event listeners
                placemat.current.removeEventListener("mouseup", stopDragging)
                placemat.current.removeEventListener("mouseleave", stopDragging)
            }
            // all done
            return
        }
    }, [viewports, activeViewport])

    // the mouse move listener is attached separately because it depends on the dragging state
    React.useEffect(() => {
        // get the active viewport ref
        const viewport = viewports[activeViewport]
        // if we don't have one
        if (!viewport) {
            // bail
            return
        }
        // move the viewport ref
        const drag = evt => {
            // if we are not dragging the viewport ref
            if (!dragging) {
                return
            }
            // otherwise, get the position of the mouse
            const x = evt.clientX
            const y = evt.clientY
            // compute the displacement in viewport pixels since the last time we took a measurement
            const dx = x - cursor.current.x
            const dy = y - cursor.current.y
            // ask the active viewport to scroll by this much
            viewport.scrollLeft += dx / (ils * scale * zoomX)
            viewport.scrollTop += dy / (ils * scale * zoomY)
            // record the event location
            cursor.current = { x, y }
            // all done
            return
        }
        // attach the mouse movement handler to the placemat
        placemat.current.addEventListener("mousemove", drag)
        // register the clean up
        return () => {
            // if the placemat is still around
            if (placemat.current) {
                // remove the mouse movement listener
                placemat.current.removeEventListener("mousemove", drag)
            }
            // all done
            return
        }

    }, [viewports, activeViewport, dragging, scale])

    // render
    return (
        <g ref={placemat}>
            <Placemat x={0} y={0} width={1} height={1} />
            <Data x={0} y={0} width={dWidth * scale} height={dHeight * scale} />
            <Viewport ref={rep} x={zoomX * x * scale} y={zoomY * y * scale}
                width={zoomX * width * scale} height={zoomY * height * scale} />
        </g>
    )
}


// the helpers
const Placemat = styled.rect`
    fill: hsl(0deg, 0%, 7%);
`

const Viewport = styled.rect`
    fill: hsl(0deg, 0%, 0%, 0%);

    stroke: ${theme.page.name};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;

    cursor: pointer;
`

const Data = styled.rect`
    fill: hsl(0deg, 0%, 15%);
`

// end of file
