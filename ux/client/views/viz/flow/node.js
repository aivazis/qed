// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the camera, which maps the pointer to diagram coordinates
import { useCamera } from '~/widgets/camera'

// local
// hooks
import { useSelection } from './useSelection'
import { useMoveNode } from './useMoveNode'


// position a node on the diagram, and let the user pick it and drag it around
export const Node = ({ id, position, children }) => {
    // unpack the position of the node
    const { x, y, z } = position
    // the map from the pointer to diagram coordinates, rounded onto the grid
    const { toICS } = useCamera()
    // access the selection
    const { select } = useSelection()
    // and the mover
    const { move } = useMoveNode()
    // where the drag started, in diagram coordinates, while there is one
    const grab = React.useRef(null)
    // how far the node has been dragged, in diagram coordinates
    const [shift, setShift] = React.useState({ dx: 0, dy: 0 })

    // a press with the main button starts a drag
    const onPointerDown = evt => {
        // only the main button drags
        if (evt.button !== 0) {
            // leave the others alone
            return
        }
        // the canvas has behaviors of its own, so keep this to myself
        evt.stopPropagation()
        // and keep the browser from starting a selection or a native drag
        evt.preventDefault()
        // follow the pointer wherever it goes until it lets go
        evt.currentTarget.setPointerCapture(evt.pointerId)
        // remember where the drag started; the node keeps its distance from the pointer
        grab.current = toICS({ x: evt.clientX, y: evt.clientY })
        // all done
        return
    }
    // a move while the node is held drags it along, snapped to the grid
    const onPointerMove = evt => {
        // if i am not being dragged
        if (grab.current === null) {
            // there is nothing to do
            return
        }
        // where the pointer is now
        const here = toICS({ x: evt.clientX, y: evt.clientY })
        // shift the node by as much as the pointer moved
        setShift({ dx: here.x - grab.current.x, dy: here.y - grab.current.y })
        // all done
        return
    }
    // letting go ends the drag; if the node moved, the server learns where it landed
    const onPointerUp = evt => {
        // if i was not being dragged
        if (grab.current === null) {
            // there is nothing to do
            return
        }
        // the drag is over
        grab.current = null
        evt.currentTarget.releasePointerCapture(evt.pointerId)
        // if the node did not move
        if (shift.dx === 0 && shift.dy === 0) {
            // there is nothing to report
            return
        }
        // otherwise, ask the server to move it, and keep it where it was dropped until the
        // server's diagram replaces the one on screen
        move(
            { id, x: x + shift.dx, y: y + shift.dy, z },
            () => setShift({ dx: 0, dy: 0 }),
        )
        // all done
        return
    }
    // a click picks me; with <shift>, it adds me to the selection or drops me from it
    const onClick = evt => {
        // the canvas clears the selection on a click, so keep this one to myself
        evt.stopPropagation()
        // pick me
        select(id, evt.shiftKey)
        // all done
        return
    }

    // build the positioning transform, including the drag in progress
    const xform = `translate(${x + shift.dx} ${y + shift.dy})`
    // node controls
    const nodeControls = { onClick, onPointerDown, onPointerMove, onPointerUp }
    // render
    return (
        <g transform={xform} {...nodeControls} >
            {children}
        </g>
    )
}

// end of file
