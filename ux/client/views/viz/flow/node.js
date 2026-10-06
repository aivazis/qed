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
import { useDiagram } from './diagram'
import { useProjection } from './projection'
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
    const { selection, select } = useSelection()
    // the mover
    const { move, step } = useMoveNode()
    // whether the server hears every step of a drag
    const { live } = useDiagram()
    // the projection, which places me on the screen and maps the pointer back onto the floor
    const { name: view, project, ground, lift } = useProjection()
    // the drag in progress, which the connectors and labels attached to me follow as well
    const { drag, setDrag, shiftOf, verdictOf, groupOf } = useDrag()
    // where the pointer grabbed me and where i was then, in diagram coordinates, during a drag,
    // along with the picked nodes i take along, if any
    const grab = React.useRef(null)
    // whether the last drag moved the selection, whose closing click must leave the picks alone
    const moved = React.useRef(false)
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
        setDrag(old => (old !== null && old.id === id) ? { ...old, ax: x, ay: y, az: z } : old)
        // all done
        return
    }, [x, y, z])

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
        grab.current = {
            pointer: toICS({ x: evt.clientX, y: evt.clientY }, false), x, y, z,
            group: groupOf(id, selection),
        }
        // and nothing has moved yet
        moved.current = false
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
        // how far the pointer moved on the screen
        const travel = { dx: here.x - grab.current.pointer.x, dy: here.y - grab.current.pointer.y }
        // with <alt>, in a view that shows heights, the pointer lifts me up or lowers me down
        const raising = evt.altKey && view !== "flat"
        // the displacement on the floor that the pointer asks for
        const shove = raising ? { dx: 0, dy: 0 } : ground(travel)
        // where i am headed: where i was, shifted by as much as the pointer moved, on the grid
        const tx = Math.round(grab.current.x + shove.dx)
        const ty = Math.round(grab.current.y + shove.dy)
        // and how high
        const tz = raising ? Math.round(grab.current.z + lift(travel.dy)) : grab.current.z
        // if that is where i was already headed
        if (dragging && drag.tx === tx && drag.ty === ty && drag.tz === tz) {
            // there is nothing new to report
            return
        }
        // the picked nodes i take along, if any
        const group = grab.current.group
        // record it, along with where the server has me
        setDrag({ id, tx, ty, tz, ax: x, ay: y, az: z, group })
        // a drag of the selection keeps the picks when it ends
        moved.current = group !== null
        // on a live canvas, the server hears every step
        if (live) {
            // so tell it
            step({ id, x: tx, y: ty, z: tz, group })
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
        const target = dragging
            ? { tx: drag.tx, ty: drag.ty, tz: drag.tz }
            : { tx: start.x, ty: start.y, tz: start.z }
        // if i ended up where i started
        if (target.tx === start.x && target.ty === start.y && target.tz === start.z && !live) {
            // there is nothing to report, and nothing being dragged
            setDrag(null)
            // all done
            return
        }
        // otherwise, ask the server to land me there, and keep me there until its diagram
        // replaces the one on screen
        move({ id, x: target.tx, y: target.ty, z: target.tz, group: start.group }, () => setDrag(null))
        // all done
        return
    }
    // a click picks me; with <shift>, it adds me to the selection or drops me from it
    const onClick = evt => {
        // the canvas clears the selection on a click, so keep this one to myself
        evt.stopPropagation()
        // the click that ends a drag of the selection
        if (moved.current) {
            // is spent
            moved.current = false
            // and leaves the picks alone
            return
        }
        // pick me
        select(id, evt.shiftKey)
        // all done
        return
    }

    // how far i am from where i am headed
    const shift = shiftOf(id)
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
    // where i am, including the drag in progress
    const [px, py, pz] = [x + shift.dx, y + shift.dy, z + shift.dz]
    // where that lands on the screen
    const spot = project({ x: px, y: py, z: pz })
    // build the positioning transform
    const xform = `translate(${spot.x} ${spot.y})`
    // when i am off the floor in a view that shows it, a stalk drops from me to my footprint
    const floor = project({ x: px, y: py, z: 0 })
    const stalk = view !== "flat" && pz !== 0 ? { x: floor.x - spot.x, y: floor.y - spot.y } : null
    // node controls
    const nodeControls = { onClick, onPointerDown, onPointerMove, onPointerUp }
    // render
    return (
        <g transform={xform} {...markers} {...nodeControls} >
            {/* the stalk and the footprint of a node off the floor */}
            {stalk && <line x1="0" y1="0" x2={stalk.x} y2={stalk.y} style={styles.iso.stalk} />}
            {stalk && <ellipse cx={stalk.x} cy={stalk.y} rx="0.6" ry="0.35" style={styles.iso.footprint} />}
            {children}
            {/* what the drop in progress would do: merge with me, or be sent back */}
            {verdict && <circle cx="0" cy="0" r="0.9" style={styles.drop[verdict]} />}
        </g>
    )
}

// end of file
