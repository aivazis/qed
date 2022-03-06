// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useEvent } from '~/hooks'
// widgets
import { SVG } from '~/widgets'

// locals
// context
import { Provider } from './context'
// hooks
import { useClearSelection } from './useClearSelection'
import { useMoving } from './useMoving'
import { usePixelPath } from './usePixelPath'
import { useSelection } from './useSelection'
import { useSetPixelPath } from './useSetPixelPath'
import { useStopMoving } from './useStopMoving'
// components
import { Labels } from './labels'
import { Mark } from './mark'
import { Path } from './path'
// styles
import styles from './styles'


// the layer
export const Measure = (props) => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Panel {...props} />
        </Provider>
    )
}


// the panel renderer
const Panel = ({ shape, raster, zoom }) => {
    // make a ref for my client area
    const me = React.useRef(null)
    // get the list of points on the profile
    const points = usePixelPath()
    // and the handler that adds points to the profile
    const { add: addPoint, displace } = useSetPixelPath()
    // get the movement marker
    const moving = useMoving()
    // and its mutator
    const stopMoving = useStopMoving()
    // get the current selection
    const selection = useSelection()
    // and the handler that clears it
    const clearSelection = useClearSelection()

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
            const p = [scale * offsetX, scale * offsetY]
            // add to my pile
            addPoint(p)
            // all done
            return
        }

        // the default action is to clear the selection
        clearSelection()

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
        triggers: [zoom]
    })

    // dragging happens when mouse move events are delivered
    useEvent({
        name: "mousemove", listener: drag, client: me,
        triggers: [zoom, moving, points, selection]
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

    // mix my paint
    const paint = styles.measure(raster)
    // and render
    return (
        <SVG ref={me} style={paint}>
            {/* join the points with a line */}
            <Path points={projected} />
            {/* add their labels */}
            <Labels positions={projected} values={points} />
            {/* and draw markers for them */}
            {projected.map((point, idx) => {
                // render a circle
                return <Mark key={idx} idx={idx} at={point} />
            })}
        </SVG>
    )
}


// end of file
