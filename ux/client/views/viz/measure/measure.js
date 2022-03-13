// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useEvent } from '~/hooks'
// widgets
import { SVG } from '~/widgets'

// locals
// context
import { Provider } from './context'
// hooks
import { useClearPixelPathSelection } from '../viz/useClearPixelPathSelection'
import { useMoving } from './useMoving'
import { usePixelPath } from '../viz/usePixelPath'
import { usePixelPathSelection } from '../viz/usePixelPathSelection'
import { useSetPixelPath } from '../viz/useSetPixelPath'
import { useStopMoving } from './useStopMoving'
// components
import { Labels } from './labels'
import { Mark } from './mark'
import { Path } from './path'


// the layer
export const Measure = (props) => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Layer {...props} />
        </Provider>
    )
}


// the layer implementation
const Layer = ({ viewport, shape, zoom }) => {
    // make a ref for my client area
    const me = React.useRef(null)
    // get the list of points on the profile
    const points = usePixelPath(viewport)
    // and the handler that adds points to the profile
    const { add: addPoint, displace } = useSetPixelPath(viewport)
    // get the movement marker
    const moving = useMoving()
    // and its mutator
    const stopMoving = useStopMoving()
    // get the current selection
    const selection = usePixelPathSelection(viewport)
    // and the handler that clears it
    const clearSelection = useClearPixelPathSelection(viewport)

    // convert the zoom level to a scaling factor
    const scale = 2 ** zoom
    // and project the points back into screen coordinates
    const projected = points.map(point => point.map(coord => Math.trunc(coord / scale)))

    // add a point to the pile
    const pick = evt => {
        // check the status of the <Alt> key
        const { altKey } = evt

        // if <alt> is pressed
        if (altKey) {
            // unpack the mouse coordinates relative to ULC of the client area
            const { offsetX, offsetY } = evt
            // scale and pack
            const p = [scale * offsetY, scale * offsetX]
            // add to my pile
            addPoint(p)
            // all done
            return
        }

        // the default action is to clear the selection
        // disabled for now, until we check with actual users
        // clearSelection()

        // all done
        return
    }

    // move
    const drag = evt => {
        // if the moving indicator is in its trivial state
        if (moving === null) {
            // bail
            return
        }
        // compute the set of nodes we will displace
        const nodes = selection.has(moving) ? [...selection] : [moving]
        // unpack the displacement from the event info
        const { movementX, movementY } = evt
        // displace
        displace({ nodes, delta: { x: scale * movementX, y: scale * movementY } })
        // all done
        return
    }

    // stop moving
    const stop = evt => {
        // clear the movement indicator
        stopMoving()
        // all done
        return
    }

    // mouse event listeners
    // when the user clicks in my area
    useEvent({
        name: "click", listener: pick, client: me,
        triggers: [viewport, zoom, addPoint]
    })

    // dragging happens when mouse move events are delivered
    useEvent({
        name: "mousemove", listener: drag, client: me,
        triggers: [viewport, zoom, moving, points, selection, displace]
    })

    // dragging ends when the user lets go of the mouse button
    useEvent({
        name: "mouseup", listener: stop, client: me,
        triggets: [selection]
    })
    // or when the mouse leaves my client area
    useEvent({
        name: "mouseleave", listener: stop, client: me,
        triggers: [selection]
    })

    // and render
    return (
        <Placemat ref={me} shape={shape}>
            {/* join the points with a line */}
            <Path points={projected} />
            {/* add their labels */}
            <Labels positions={projected} values={points} />
            {/* and draw markers for them */}
            {projected.map((point, idx) => {
                // render a circle
                return <Mark key={idx} idx={idx} at={point} viewport={viewport} />
            })}
        </Placemat>
    )
}


// my placemat
const Placemat = styled(SVG)`
    position: absolute;
    top: 0px;
    left: 0px;
    width: ${props => props.shape[1]}px;
    height: ${props => props.shape[0]}px;
`


// end of file
