// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
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
import { useAnchorAdd } from './useAnchorAdd'
import { useAnchorDrag } from './useAnchorDrag'
import { useAnchorMove } from './useAnchorMove'
// components
import { Anchor } from './anchor'
import { Labels } from './labels'
import { Path } from './path'


// the layer
export const Measure = props => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Layer {...props} />
        </Provider>
    )
}


// the layer implementation
//
// {scale} enables the conversion from zoomed screen coordinates to image coordinates
//
const Layer = ({ viewport, view, shape, scale }) => {
    // unpack the {view}
    const { measure } = useFragment(measureGetMeasureLayerFragment, view)
    // make a ref for my client area
    const me = React.useRef(null)
    // get anchor movement support
    const { dragging, stop } = useAnchorDrag()
    // the anchor interface
    const { add } = useAnchorAdd(viewport)
    // the anchor mover
    const { move } = useAnchorMove(viewport)

    // unpack the measure layer info
    const { path, selection, closed } = measure
    // convert the path into an array of (lines, samples) pairs
    const anchors = path.map(anchor => [anchor.x, anchor.y])
    // project the points back into screen coordinates
    const projected = anchors.map(
        anchor => anchor.map((coord, idx) => Math.trunc(coord / scale[idx]))
    )

    // add an anchor to the pile
    const pick = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // get the status of the <Alt> key
        const { altKey } = evt
        // if <Alt> is pressed
        if (altKey) {
            // unpack the pointer coordinates relative to the ULC of the client area
            const { offsetX, offsetY } = evt
            // scale and pack
            const anchor = {
                x: scale[1] * offsetX,
                y: scale[0] * offsetY,
            }
            // add it to the pile
            add(anchor)
            // all done
            return
        }

        // the default action is to clear the selection
        // disabled for now, until we check with actual users
        // clearSelection()

        // all done
        return
    }

    // move an anchor
    const displace = evt => {
        // N.B.:
        //   do NOT stop the propagation of this event
        //   the {viewer} layer below {measure} uses it to keep track and display the
        //   cursor location
        // unpack
        const { offsetX, offsetY } = evt
        // if the moving indicator is in its trivial state
        if (dragging === null) {
            // bail
            return
        }
        // compute the displacement implied by the current position of the cursor
        const delta = {
            x: scale[1] * offsetX - path[dragging].x,
            y: scale[0] * offsetY - path[dragging].y,
        }
        // check for null displacement
        if (Math.abs(delta.x) < 1 && Math.abs(delta.y) < 1) {
            // and avoid repainting
            return
        }
        // if there is real work, displace the selection
        move({ handle: dragging, delta })
        // all done
        return
    }

    // stop moving
    const drop = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // clear the movement indicator
        stop()
        // all done
        return
    }

    // mouse event listeners
    // when the user clicks in my area
    useEvent({
        name: "mouseup", listener: pick, client: me,
        triggers: [viewport, scale, add]
    })

    // dragging happens when mouse move events are delivered
    useEvent({
        name: "mousemove", listener: displace, client: me,
        triggers: [viewport, scale, dragging, path, selection, displace]
    })

    // dragging ends when the user lets go of the mouse button
    useEvent({
        name: "mouseup", listener: drop, client: me,
        triggers: [selection]
    })
    // or when the mouse leaves my client area
    useEvent({
        name: "mouseleave", listener: drop, client: me,
        triggers: [selection]
    })

    // render
    return (
        <Placemat ref={me} shape={shape}>
            {/* join the points with a line */}
            <Path points={projected} closed={closed} />
            {/* add their labels */}
            <Labels positions={projected} values={anchors} />
            {/* and draw markers for them */}
            {projected.map((point, idx) => {
                // render a circle
                return (
                    <Anchor key={idx}
                        viewport={viewport} selection={selection} idx={idx} at={point}
                    />
                )
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

// my fragment
const measureGetMeasureLayerFragment = graphql`
    fragment measureGetMeasureLayerFragment on View {
        measure {
            closed
            path {
                x
                y
            }
            selection
        }
    }
`

// end of file
