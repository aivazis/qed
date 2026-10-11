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
// the projection
import { ProjectionProvider, makeProjection } from './projection'
// the scenes of the views
import { FlatScene } from './flat/scene'
import { IsoScene } from './iso/scene'
// the drag in progress
import { DragProvider } from './drag'
// the drop target for factories from the palette
import { Drops } from './drops'
// the editor
import { useEditDiagram } from './useEditDiagram'
// the fan that refines a factory in place
import { Fan, FanProvider, useFanState } from './fan'
// paint
import styles from './styles'


// the canvas that draws a pipeline {diagram} and lets the user edit it; when {live}, every step of
// a drag goes to the server; whenever {focusOn} changes, i take the focus; with {onCamera}, my
// camera is shared: every move of it is told to {onCamera}, and it looks where {camera} says; with
// a {catalog} of what each protocol can be pinned to, a factory of an editable diagram fans out
// the choices that refine it
export const Canvas = ({
    diagram: diagramRef, live = false, view = { kind: "flat" }, focusOn, camera, onCamera, catalog,
}) => {
    // get the diagram
    const diagram = useFragment(canvasFlowDiagramFragment, diagramRef)
    // build a reference to my container so we can measure it and install listeners
    const ref = React.useRef(null)
    // the projection the {view} asks for
    const projection = makeProjection(view)
    // and whether it is flat
    const flat = projection.name === "flat"
    // where it puts points
    const { project } = projection
    // the camera looks at the middle of the diagram, as projected
    const focus = center(diagram, project)
    // whether i have drawn before, so that the first drawing does not take the focus
    const drawn = React.useRef(false)
    // my owner says when to take the focus: after a click on the controls of the view, which took
    // it away from me, so the keys of the camera keep working in the new view
    React.useEffect(() => {
        // the first drawing leaves the focus where it is
        if (!drawn.current) {
            // but remembers that it happened
            drawn.current = true
            // and stops
            return
        }
        // otherwise, take the focus, without scrolling me into view
        ref.current?.focus({ preventScroll: true })
        // all done
        return
    }, [focusOn])
    // the nodes a drag can land on, with what decides whether it may
    const nodes = occupants(diagram)
    // the factories each slot connects to
    const owners = ownership(diagram)
    // the slots each factory takes along when it moves
    const followers = entourage(diagram, owners)
    // whether the structure of the diagram can change
    const editable = diagram?.editable ?? false
    // the fan, which only an editable diagram with a catalog has
    const fan = useFanState({
        factories: diagram?.factories ?? [], catalog: editable ? catalog : null,
    })

    // access the selection
    const { selection, clear } = useSelection()
    // the editor
    const { remove } = useEditDiagram(diagram?.id ?? null)
    // <enter> fans out the picked factory, <escape> folds the fan, and the delete keys remove the
    // picked factories
    const onKeyDown = evt => {
        // a fan that is out
        if (fan.factory && evt.key === "Escape") {
            // folds
            fan.close()
            // all done
            return
        }
        // the factory that is picked on its own
        const picked = selection.length === 1
            ? diagram?.factories.find(factory => factory.id === selection[0])
            : null
        // fans out on <enter>
        if (picked && evt.key === "Enter") {
            // so fan it out, or fold it if it is out already
            fan.factory?.id === picked.id ? fan.close() : fan.open(picked.id)
            // all done
            return
        }
        // if it is not one of the delete keys, or the diagram cannot be edited
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
    // a click on the canvas, away from any node, folds the fan, or else clears the selection
    const clearSelection = () => {
        // a fan that is out
        if (fan.factory) {
            // folds, and leaves the selection alone
            fan.close()
            // all done
            return
        }
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
                <Camera ref={ref} scale={20} focus={focus} focusKey={`${diagram?.id}:${projection.key}`}
                    shared={camera} onSettle={onCamera}>
                    {/* the way the diagram is drawn */}
                    <ProjectionProvider projection={projection}>
                        {/* the diagram, which the requests that change it name */}
                        <DiagramProvider id={diagram?.id ?? null} live={live}>
                            {/* the drop target for factories from the palette, when it can be edited */}
                            {editable && <Drops canvas={ref} />}
                            {/* the drag in progress, which the nodes publish and the rest follow */}
                            <DragProvider nodes={nodes} followers={followers} owners={owners}
                                editable={editable}>
                                {/* the fan, which the nodes open */}
                                <FanProvider fan={fan}>
                                    {/* the diagram, as the view in use draws it, faded while a fan is out */}
                                    <g opacity={fan.factory ? styles.fan.dim : 1}>
                                        {flat
                                            ? <FlatScene diagram={diagram} />
                                            : <IsoScene diagram={diagram} nodes={nodes} />}
                                    </g>
                                    {/* and the fan itself, over it */}
                                    <Fan />
                                </FanProvider>
                            </DragProvider>
                        </DiagramProvider>
                    </ProjectionProvider>
                </Camera>
            </svg>
        </section>

    )
}

// the middle of the box that holds the factories and slots of a {diagram}, as {project}ed onto the
// screen, or nothing for a diagram that is missing or empty
const center = (diagram, project) => {
    // the positions of the nodes, on the screen
    const points = diagram ? [...diagram.factories, ...diagram.slots].map(node => project(node.at)) : []
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
        # can tell what it is about to land on; and what the factories are, so the fan can offer
        # what refines them
        factories {
            id
            family
            protocol
            level
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
        # all the nodes, for the isometric view
        ...sceneFlowDiagramFragment
    }
`


// end of file
