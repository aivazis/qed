// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// the node being dragged on the pipeline diagram: where it is headed, and where the server has it
// now, both in diagram coordinates; the connectors and labels attached to it read it, so they
// follow the node while it moves. the shift is the difference of the two, so a server that moves
// the node mid-drag, as it does for a live viewport, never makes it travel twice
const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // nothing is being dragged
        drag: null,
        setDrag: () => { throw new Error('no drag provider') },
        // so there is no landing to judge
        landing: null,
    }
)


// the provider; {nodes} are the nodes a drag can land on, with what decides whether it may
export const DragProvider = ({ nodes = [], children }) => {
    // the drag in progress, as { id, tx, ty, ax, ay }, or nothing
    const [drag, setDrag] = React.useState(null)
    // what a drop where the dragged node is headed would do
    const landing = judge(drag, nodes)
    // provide for my children
    return (
        <Context.Provider value={{ drag, setDrag, landing }}>
            {children}
        </Context.Provider>
    )
}


// access to the drag in progress
export const useDrag = () => {
    // pull it from the context
    const { drag, setDrag, landing } = React.useContext(Context)
    // how far the node with {id} is from where it is headed, which is nowhere unless it is the
    // one being dragged
    const shiftOf = id => (drag !== null && drag.id === id)
        ? { dx: drag.tx - drag.ax, dy: drag.ty - drag.ay }
        : { dx: 0, dy: 0 }
    // what the drop would do, as seen by the node with {id}: the node it would land on hears
    // "merge" or "blocked", and so does the dragged node when it would be sent back
    const verdictOf = id => {
        // without a node to land on, there is nothing to say
        if (landing === null) {
            // so say nothing
            return null
        }
        // the node it would land on
        if (landing.occupant === id) {
            // hears the verdict
            return landing.verdict
        }
        // the dragged node hears only that it would be sent back
        if (drag.id === id && landing.verdict === "blocked") {
            // so tell it
            return "blocked"
        }
        // nobody else is involved
        return null
    }
    // publish
    return { drag, setDrag, shiftOf, verdictOf }
}


// decide what dropping the dragged node where it is headed would do, by the rule the server
// applies: nothing to say on an empty spot; a factory takes no company, and neither do two slots
// that both carry products; anything else merges
const judge = (drag, nodes) => {
    // without a drag, there is no landing
    if (drag === null) {
        // so say so
        return null
    }
    // the node being dragged
    const mover = nodes.find(node => node.id === drag.id)
    // if it is not on the diagram, e.g. because the diagram just changed
    if (!mover) {
        // there is nothing to say
        return null
    }
    // the node already where it is headed, if any
    const occupant = nodes.find(node =>
        node.id !== mover.id && node.x === drag.tx && node.y === drag.ty && node.z === mover.z)
    // an empty spot
    if (!occupant) {
        // is a plain move
        return null
    }
    // a factory on either side, or two slots that both carry products, cannot share a spot
    const blocked = mover.kind === "factory" || occupant.kind === "factory"
        || (mover.bound && occupant.bound)
    // render the verdict
    return { occupant: occupant.id, verdict: blocked ? "blocked" : "merge" }
}


// end of file
