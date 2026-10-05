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
// the active viewport, and whether it syncs live
import { useViewports } from '../viz/useViewports'
import { useLive } from '../viz/useLive'

// local
// hooks
import { useSelection } from './useSelection'
import { useMoveNode } from './useMoveNode'
import { useDrag } from './drag'
// styles
import styles from './styles'


// position a node on the diagram, and let the user pick it and drag it around
export const Node = ({ id, kind, position, handles = {}, children }) => {
    // unpack the position of the node, as the server has it
    const { x, y, z } = position
    // the map from the pointer to diagram coordinates, rounded onto the grid
    const { toICS } = useCamera()
    // access the selection
    const { select } = useSelection()
    // the mover
    const { move, step } = useMoveNode()
    // whether my viewport syncs live, in which case the server hears every step of a drag
    const { activeViewport } = useViewports()
    const { enabled: live } = useLive(activeViewport)
    // the drag in progress, which the connectors and labels attached to me follow as well
    const { drag, setDrag, shiftOf, verdictOf } = useDrag()
    // where the pointer grabbed me and where i was then, in diagram coordinates, during a drag
    const grab = React.useRef(null)
    // whether i am the node being dragged
    const dragging = drag !== null && drag.id === id

    // while i am being dragged, keep the drag informed of where the server has me, so the shift
    // stays the distance to where i am headed even when the server moves me mid-drag
    React.useEffect(() => {
        // if i am not being dragged
        if (!dragging) {
            // there is nothing to report
            return
        }
        // otherwise, record where the server has me now
        setDrag(old => (old !== null && old.id === id) ? { ...old, ax: x, ay: y } : old)
        // all done
        return
    }, [x, y])

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
        // which also keeps the canvas from taking the focus, so hand it over explicitly: the delete
        // keys and the camera keys listen there
        evt.currentTarget.closest("section")?.focus()
        // follow the pointer wherever it goes until it lets go
        evt.currentTarget.setPointerCapture(evt.pointerId)
        // remember where the pointer grabbed me and where i was; i keep my distance from it
        grab.current = { pointer: toICS({ x: evt.clientX, y: evt.clientY }, false), x, y }
        // all done
        return
    }
    // a move while i am held drags me along, snapped to the grid
    const onPointerMove = evt => {
        // if i am not being dragged
        if (grab.current === null) {
            // there is nothing to do
            return
        }
        // where the pointer is now
        const here = toICS({ x: evt.clientX, y: evt.clientY }, false)
        // where i am headed: where i was, shifted by as much as the pointer moved, on the grid
        const tx = Math.round(grab.current.x + here.x - grab.current.pointer.x)
        const ty = Math.round(grab.current.y + here.y - grab.current.pointer.y)
        // if that is where i was already headed
        if (dragging && drag.tx === tx && drag.ty === ty) {
            // there is nothing new to report
            return
        }
        // record it, along with where the server has me
        setDrag({ id, tx, ty, ax: x, ay: y })
        // in a live viewport, the server hears every step
        if (live) {
            // so tell it
            step({ id, x: tx, y: ty, z })
        }
        // all done
        return
    }
    // letting go ends the drag; if i moved, the server learns where i landed
    const onPointerUp = evt => {
        // if i was not being dragged
        if (grab.current === null) {
            // there is nothing to do
            return
        }
        // the drag is over
        const start = grab.current
        grab.current = null
        evt.currentTarget.releasePointerCapture(evt.pointerId)
        // where i was headed
        const target = dragging ? { tx: drag.tx, ty: drag.ty } : { tx: start.x, ty: start.y }
        // if i ended up where i started
        if (target.tx === start.x && target.ty === start.y && !live) {
            // there is nothing to report, and nothing being dragged
            setDrag(null)
            // all done
            return
        }
        // otherwise, ask the server to land me there, and keep me there until its diagram
        // replaces the one on screen
        move({ id, x: target.tx, y: target.ty, z }, () => setDrag(null))
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

    // how far i am from where i am headed
    const shift = shiftOf(id)
    // whether i am picked
    const { selection } = useSelection()
    // what the drop in progress would do to me, if anything
    const verdict = verdictOf(id)
    // the handles that let a script find me and read my state: who i am, what i am, where the
    // server has me, and whether i am picked, along with whatever my kind adds
    const markers = {
        "data-qed-node": id,
        "data-qed-kind": kind,
        "data-qed-at": `${x},${y},${z}`,
        "data-qed-selected": selection.includes(id),
        "data-qed-drop": verdict ?? undefined,
        ...handles,
    }
    // build the positioning transform, including the drag in progress
    const xform = `translate(${x + shift.dx} ${y + shift.dy})`
    // node controls
    const nodeControls = { onClick, onPointerDown, onPointerMove, onPointerUp }
    // render
    return (
        <g transform={xform} {...markers} {...nodeControls} >
            {children}
            {/* what the drop in progress would do: merge with me, or be sent back */}
            {verdict && <circle cx="0" cy="0" r="0.9" style={styles.drop[verdict]} />}
        </g>
    )
}

// end of file
