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
        // and nobody follows anybody
        followers: {},
    }
)


// the provider; {nodes} are the nodes a drag can land on, with what decides whether it may, and
// {followers} are the slots each factory takes along when it moves
export const DragProvider = ({ nodes = [], followers = {}, children }) => {
    // the drag in progress, as { id, tx, ty, ax, ay }, or nothing
    const [drag, setDrag] = React.useState(null)
    // what a drop where the dragged node is headed would do
    const landing = judge(drag, nodes, followers)
    // provide for my children
    return (
        <Context.Provider value={{ drag, setDrag, landing, followers }}>
            {children}
        </Context.Provider>
    )
}


// access to the drag in progress
export const useDrag = () => {
    // pull it from the context
    const { drag, setDrag, landing, followers } = React.useContext(Context)
    // how far the node with {id} is from where it is headed, which is nowhere unless it is the
    // one being dragged, or one of the slots it takes along
    const shiftOf = id => (drag !== null && (drag.id === id || followers[drag.id]?.includes(id)))
        ? { dx: drag.tx - drag.ax, dy: drag.ty - drag.ay }
        : { dx: 0, dy: 0 }
    // what the drop would do, as seen by the node with {id}: every node involved in it hears
    // "merge" or "blocked", and nobody else hears anything
    const verdictOf = id => landing?.[id] ?? null
    // publish
    return { drag, setDrag, shiftOf, verdictOf }
}


// decide what dropping the dragged node where it is headed would do, by the rule the server
// applies: nothing to say on an empty spot; a factory takes no company, and neither do two slots
// that both carry products; anything else merges. a factory moves along with its own slots, so
// it is sent back if any of them would land on somebody else. the verdict maps every node
// involved to what it would see: the obstacles, the members of the group that would hit them, and
// the dragged node itself
const judge = (drag, nodes, followers) => {
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
    // the members of the group that moves
    const group = new Set([mover.id, ...(followers[mover.id] ?? [])])
    // whoever, outside the group, sits at a spot
    const at = (x, y, z) => nodes.find(node => !group.has(node.id) && node.x === x && node.y === y && node.z === z)
    // how far the group moves
    const [dx, dy] = [drag.tx - mover.x, drag.ty - mover.y]
    // the verdicts, by node
    const verdicts = {}
    // go through the slots that follow the mover
    for (const id of group) {
        // skipping the mover itself, whose landing is judged below
        if (id === mover.id) {
            // on to the next
            continue
        }
        // the member
        const member = nodes.find(node => node.id === id)
        // whoever it would land on
        const other = member ? at(member.x + dx, member.y + dy, member.z) : null
        // a follower lands on somebody
        if (other) {
            // both of them see the collision
            verdicts[other.id] = "blocked"
            verdicts[member.id] = "blocked"
        }
    }
    // the node already where the mover is headed, if any
    const occupant = at(drag.tx, drag.ty, mover.z)
    // if there is one
    if (occupant) {
        // a factory on either side, or two slots that both carry products, cannot share a spot
        const blocked = mover.kind === "factory" || occupant.kind === "factory"
            || (mover.bound && occupant.bound)
        // record what the occupant sees
        verdicts[occupant.id] = blocked ? "blocked" : "merge"
    }
    // if anything is blocked, the whole move is sent back
    if (Object.values(verdicts).includes("blocked")) {
        // which the mover hears as well
        verdicts[mover.id] = "blocked"
        // and a merge that will not happen is not worth advertising
        for (const [id, verdict] of Object.entries(verdicts)) {
            // so turn it off
            if (verdict === "merge") {
                delete verdicts[id]
            }
        }
    }
    // an empty verdict means a plain move
    return Object.keys(verdicts).length ? verdicts : null
}


// end of file
