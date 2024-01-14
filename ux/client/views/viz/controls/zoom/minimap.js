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


// export the minimap
export const Minimap = ({ shape, zoom }) => {
    // we have
    // - the shape of the dataset in the active view
    // - the current zoom level
    // we need
    // - the origin + shape of the active viewport

    // get the viewport information
    const { activeViewport, viewports } = useViewports()
    // build a listener that tracks the size of the active viewport
    // and one that tracks its origin

    // install the trackers on the active viewport
    React.useEffect(() => {
        // get the active viewport ref
        const target = viewports[activeViewport]
        // show me
        console.log(target)
        // get the position of the view
        const viewLeft = target.scrollLeft
        const viewTop = target.scrollTop
        // measure it
        // N.B.: don't be tempted to spread the return; MDN claims it doesn't work...
        const box = target.getBoundingClientRect()
        // get the shape of the view
        const viewWidth = box.width
        const viewHeight = box.height
        // show me
        console.log(`dataset shape: ${shape}`)
        console.log(`zoom level: ${zoom}`)
        console.log(`view: ${viewHeight}x${viewWidth}+${viewLeft}x${viewTop}`)

        // make an abort controller
        const controller = new AbortController()

        // register a clean up
        return () => {
            // that removes the listeners we installed
            // and aborts any pending requests
            controller.abort()
            // all done
            return
        }
    })

    // render
    return (
        <g>
            <Placemat x={0} y={0} width={1} height={1} />
            <Data />
            <Viewport />
        </g>
    )
}


// the helpers
const Placemat = styled.rect`
    fill: hsl(0deg, 0%, 10%);
`

const Viewport = styled.rect`
    fill: none;

    stroke: hsl(0deg, 0%, 20%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`

const Data = styled.rect`
    fill: none;

    stroke: hsl(0deg, 0%, 20%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`

// end of file
