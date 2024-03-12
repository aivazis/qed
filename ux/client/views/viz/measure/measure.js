// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
import { useMoving } from './useMoving'
import { usePixelPath } from '../../main/usePixelPath'
import { usePixelPathSelection } from '../../main/usePixelPathSelection'
import { useSetPixelPath } from '../../main/useSetPixelPath'
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
const Layer = ({ viewport, shape, scale }) => {
    // make a ref for my client area
    const me = React.useRef(null)
    // get the path spec of the current viewport
    const pixelPath = usePixelPath(viewport)
    // and the handler that adds points to the profile
    const { add: addPoint, displace } = useSetPixelPath(viewport)
    // get the movement marker
    const moving = useMoving()
    // and its mutator
    const stopMoving = useStopMoving()
    // get the current selection
    const selection = usePixelPathSelection(viewport)

    // get the list of points on the profile
    const { closed, points } = pixelPath
    // and project the points back into screen coordinates
    const projected = points.map(
        point => point.map((coord, idx) => Math.trunc(coord / scale[idx]))
    )

    // add a point to the pile
    const pick = evt => {
        // check the status of the <Alt> key
        const { altKey } = evt

        // if <alt> is pressed
        if (altKey) {
            // unpack the mouse coordinates relative to ULC of the client area
            const { offsetX, offsetY } = evt
            // scale and pack
            const p = [scale[0] * offsetY, scale[1] * offsetX]
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
    const drag = ({ offsetX, offsetY }) => {
        // if the moving indicator is in its trivial state
        if (moving === null) {
            // bail
            return
        }
        // compute the set of nodes we will displace
        const nodes = selection.has(moving) ? [...selection] : [moving]
        // compute the displacement implied by the current position of the cursor
        const delta = {
            x: scale[1] * offsetX - points[moving][1],
            y: scale[0] * offsetY - points[moving][0],
        }
        // check for null displacement
        if (Math.abs(delta.x) < 1 && Math.abs(delta.y) < 1) {
            // and avoid repainting
            return
        }
        // if there is real work, displace the selection
        displace({ nodes, delta })
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
        triggers: [viewport, scale, addPoint]
    })

    // dragging happens when mouse move events are delivered
    useEvent({
        name: "mousemove", listener: drag, client: me,
        triggers: [viewport, scale, moving, points, selection, displace]
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
            <Path points={projected} closed={closed} />
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
