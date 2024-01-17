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
export const Minimap = ({ shape, zoom }) => {
    // we have
    // - the shape of the dataset in the active view
    // - the current zoom level
    // we need
    // - the origin + shape of the active viewport

    // storage for the origin of the viewport
    const [origin, setOrigin] = React.useState({ x: 0, y: 0 })
    // and its size
    const [extent, setExtent] = React.useState({ width: 0, height: 0 })
    // get the viewport information
    const { activeViewport, viewports } = useViewports()
    // build a listener that tracks the size of the active viewport
    // and one that tracks its origin

    // install the trackers on the active viewport
    React.useEffect(() => {
        // get the active viewport ref
        const viewport = viewports[activeViewport]
        // if it's not a valid
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
        const scroll = evt => {
            // deduce the scroll position
            const origin = { x: viewport.scrollLeft, y: viewport.scrollTop }
            // update the viewport origin
            setOrigin(origin)
            // all done
            return
        }
        // by registering a listener
        viewport.addEventListener("scroll", scroll)

        // register a clean up
        return () => {
            // if we have a valid viewport
            if (viewport) {
                // disconnect it from the observer
                observer.disconnect()
                // and remove the scroll listener
                viewport.removeEventListener("scroll", scroll)
            }
            // all done
            return
        }
    }, [viewports, activeViewport])

    // unpack the dataset shape
    const [dHeight, dWidth] = shape
    // unpack the zoom
    const [zoomX, zoomY] = [2 ** zoom, 2 ** zoom]
    // unpack the viewport origin
    const { x, y } = origin
    // and its extent
    const { width, height } = extent

    // set the scale
    const scale = Math.max(dWidth, zoomX * (x + width),
        dHeight, zoomY * (y + height))

    // render
    return (
        <g>
            <Placemat x={0} y={0} width={1} height={1} />
            <Data x={0} y={0} width={dWidth / scale} height={dHeight / scale} />
            <Viewport x={zoomX * x / scale} y={zoomY * y / scale}
                width={zoomX * width / scale} height={zoomY * height / scale} />
        </g>
    )
}


// the helpers
const Placemat = styled.rect`
    fill: hsl(0deg, 0%, 7%);
`

const Viewport = styled.rect`
    fill: none;

    stroke: ${theme.page.name};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`

const Data = styled.rect`
    fill: hsl(0deg, 0%, 15%);
`

// end of file
