// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
import { Camera, Compass } from '~/widgets'

// local
// hooks
import { useSelection } from './useSelection'
// the diagram on the canvas
import { DiagramProvider } from './diagram'
// the drag in progress
import { DragProvider } from './drag'
// the drop target for factories from the palette
import { Drops } from './drops'
// the editor
import { useEditDiagram } from './useEditDiagram'
// components
import { Grid } from './grid'
// diagram nodes
import { Connectors } from './connectors'
import { Factories } from './factories'
import { Labels } from './labels'
import { Slots } from './slots'
// paint
import styles from './styles'


// the canvas that draws a pipeline {diagram} and lets the user edit it; when {live}, every step of
// a drag goes to the server
export const Canvas = ({ diagram: diagramRef, live = false }) => {
    // get the diagram
    const diagram = useFragment(canvasFlowDiagramFragment, diagramRef)
    // build a reference to my container so we can measure it and install listeners
    const ref = React.useRef(null)
    // the camera looks at the middle of the diagram
    const focus = center(diagram)
    // the nodes a drag can land on, with what decides whether it may
    const nodes = occupants(diagram)
    // the factories each slot connects to
    const owners = ownership(diagram)
    // the slots each factory takes along when it moves
    const followers = entourage(diagram, owners)
    // whether the structure of the diagram can change
    const editable = diagram?.editable ?? false

    // access the selection
    const { selection, clear } = useSelection()
    // the editor
    const { remove } = useEditDiagram(diagram?.id ?? null)
    // the delete keys remove the picked factories
    const onKeyDown = evt => {
        // if it is not one of them, or the diagram cannot be edited
        if (!editable || (evt.key !== "Delete" && evt.key !== "Backspace")) {
            // it is not for me
            return
        }
        // the nodes of this diagram
        const known = new Set([
            ...(diagram?.factories.map(factory => factory.id) ?? []),
            ...(diagram?.slots.map(slot => slot.id) ?? []),
        ])
        // remove the picked ones: a factory goes, a slot undoes its binding
        selection.filter(id => known.has(id)).forEach(remove)
        // and forget the picks
        clear()
        // all done
        return
    }
    // a click on the canvas, away from any node, clears it
    const clearSelection = () => {
        // drop the selection
        clear()
        // all done
        return
    }

    // assemble the canvas behaviors
    const behaviors = {
        // clear the selection
        onClick: clearSelection,
    }

    // render
    return (
        <section ref={ref} tabIndex="-1" style={styles.panel} onKeyDown={onKeyDown}>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                {...styles.canvas} style={styles.surface} {...behaviors}
                data-qed-diagram={diagram?.id ?? ""}
            >
                {/* everything that is in ICS */}
                <Camera ref={ref} scale={20} focus={focus} focusKey={diagram?.id}>
                    {/* the diagram, which the requests that change it name */}
                    <DiagramProvider id={diagram?.id ?? null} live={live}>
                        {/* the drop target for factories from the palette, when it can be edited */}
                        {editable && <Drops canvas={ref} />}
                        {/* the drag in progress, which the nodes publish and the rest follow */}
                        <DragProvider nodes={nodes} followers={followers} owners={owners}
                            editable={editable}>
                            {/* the orientation marker at the origin */}
                            {/* <Compass /> */}
                            {/* the current cell highlighter */}
                            <Grid />
                            {/* labels */}
                            <Labels diagram={diagram} />
                            {/* connector */}
                            <Connectors diagram={diagram} />
                            {/* slots */}
                            <Slots diagram={diagram} />
                            {/* factories */}
                            <Factories diagram={diagram} />
                        </DragProvider>
                    </DiagramProvider>
                </Camera>
            </svg>
        </section>

    )
}

// the middle of the box that holds the factories and slots of a {diagram}, or nothing for a
// diagram that is missing or empty
const center = (diagram) => {
    // the positions of the nodes
    const points = diagram ? [...diagram.factories, ...diagram.slots].map(node => node.at) : []
    // an empty diagram
    if (points.length == 0) {
        // has no middle
        return null
    }
    // the extent of the box along each axis
    const xs = points.map(point => point.x)
    const ys = points.map(point => point.y)
    // its middle
    return {
        x: (Math.min(...xs) + Math.max(...xs)) / 2,
        y: (Math.min(...ys) + Math.max(...ys)) / 2,
    }
}


// the nodes of a {diagram} that a drag can land on: where they are, what they are, and, for slots,
// whether they carry a product
const occupants = (diagram) => {
    // a missing diagram has none
    if (!diagram) {
        // so say so
        return []
    }
    // the factories
    const factories = diagram.factories.map(({ id, at }) => ({ id, kind: "factory", ...at, bound: false }))
    // the slots
    const slots = diagram.slots.map(({ id, at, bound }) => ({ id, kind: "slot", ...at, bound }))
    // all of them
    return [...factories, ...slots]
}


// the factories each slot of a {diagram} connects to, by slot
const ownership = (diagram) => {
    // the factories, by slot
    const owners = {}
    // go through the connectors, if there is a diagram
    for (const { factoryId, slotId } of diagram?.connectors ?? []) {
        // and record each connection
        owners[slotId] = (owners[slotId] ?? new Set()).add(factoryId)
    }
    // hand them off
    return owners
}


// the slots each factory of a {diagram} takes along when it moves: its own, unbound slots, the
// ones no other factory connects to, by the rule the server applies; {owners} are the factories
// each slot connects to
const entourage = (diagram, owners) => {
    // a missing diagram has none
    if (!diagram) {
        // so say so
        return {}
    }
    // the slots that carry no product
    const unbound = new Set(diagram.slots.filter(slot => !slot.bound).map(slot => slot.id))
    // the followers of each factory
    const followers = {}
    // go through the slots
    for (const [slotId, factories] of Object.entries(owners)) {
        // a slot that is unbound and connected to exactly one factory
        if (unbound.has(slotId) && factories.size === 1) {
            // follows it
            const [factoryId] = factories
            followers[factoryId] = [...(followers[factoryId] ?? []), slotId]
        }
    }
    // hand them off
    return followers
}


// my fragment
const canvasFlowDiagramFragment = graphql`
    fragment canvasFlowDiagramFragment on FlowDiagram {
        # metadata
        id
        name
        family
        # whether its structure can change
        editable
        # where the nodes are, so the camera can look at the middle of the diagram, and a drag
        # can tell what it is about to land on
        factories {
            id
            at {
                x
                y
                z
            }
        }
        slots {
            id
            at {
                x
                y
                z
            }
            bound
        }
        # which slot joins which factory, so a factory can take its own slots along
        connectors {
            factoryId
            slotId
        }
        # labels
        ...labelsFlowDiagramFragment
        # connectors
        ...connectorsFlowDiagramFragment
        # slots
        ...slotsFlowDiagramFragment
        # factories
        ...factoriesFlowDiagramFragment
    }
`


// end of file
