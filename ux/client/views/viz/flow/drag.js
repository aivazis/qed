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
        // nobody follows anybody
        followers: {},
        // no slot connects to anything
        owners: {},
        // and there are no nodes to move
        nodes: [],
    }
)


// the provider; {nodes} are the nodes a drag can land on, with what decides whether it may,
// {followers} are the slots each factory takes along when it moves, {owners} are the factories
// each slot connects to, and a diagram that is not {editable} merges nothing
export const DragProvider = ({ nodes = [], followers = {}, owners = {}, editable = true, children }) => {
    // the drag in progress, as { id, tx, ty, tz, ax, ay, az }, or nothing; a drag that moves the
    // selection also carries the picked nodes as its {group}
    const [drag, setDrag] = React.useState(null)
    // what a drop where the dragged node is headed would do
    const landing = judge(drag, nodes, followers, owners, editable)
    // provide for my children
    return (
        <Context.Provider value={{ drag, setDrag, landing, followers, owners, nodes }}>
            {children}
        </Context.Provider>
    )
}


// access to the drag in progress
export const useDrag = () => {
    // pull it from the context
    const { drag, setDrag, landing, followers, owners, nodes } = React.useContext(Context)
    // the nodes that move with the drag in progress
    const crowd = members(drag, followers, owners)
    // how far the node with {id} is from where it is headed, which is nowhere unless it is one of
    // the nodes that move
    const shiftOf = id => crowd.has(id)
        ? { dx: drag.tx - drag.ax, dy: drag.ty - drag.ay, dz: (drag.tz ?? drag.az) - drag.az }
        : { dx: 0, dy: 0, dz: 0 }
    // the picked nodes that a drag of the node with {id} would move: all of them, if it is one of
    // several picked nodes on this diagram, and none otherwise, which makes it a drag of its own
    const groupOf = (id, selection) => {
        // the nodes of this diagram
        const known = new Set(nodes.map(node => node.id))
        // the picked ones among them
        const picked = selection.filter(pick => known.has(pick))
        // a node that is not one of several picked nodes
        if (!picked.includes(id) || picked.length < 2) {
            // moves on its own
            return null
        }
        // otherwise, it takes the rest of the picks along
        return picked
    }
    // what the drop would do, as seen by the node with {id}: every node involved in it hears
    // "merge" or "blocked", and nobody else hears anything
    const verdictOf = id => landing?.[id] ?? null
    // publish
    return { drag, setDrag, shiftOf, verdictOf, groupOf }
}


// the nodes that move with a {drag}: the dragged node, along with the slots it takes along, or,
// when it moves the selection, the picked nodes along with every slot that connects only to
// picked factories, by the rule the server applies
const members = (drag, followers, owners) => {
    // without a drag
    if (drag === null) {
        // nothing moves
        return new Set()
    }
    // a drag of a single node
    if (!drag.group) {
        // moves the node and its followers
        return new Set([drag.id, ...(followers[drag.id] ?? [])])
    }
    // otherwise, the picked nodes move
    const picked = new Set(drag.group)
    // along with the slots that connect to some factories, all of them picked
    const cohort = Object.entries(owners)
        .filter(([, factories]) => factories.size > 0 && [...factories].every(id => picked.has(id)))
        .map(([slot]) => slot)
    // all of them
    return new Set([...picked, ...cohort])
}


// decide what dropping the dragged node where it is headed would do, by the rule the server
// applies: nothing to say on an empty spot; a factory takes no company, and neither do two slots
// that both carry products; anything else merges. a factory moves along with its own slots, so
// it is sent back if any of them would land on somebody else; the selection moves as a whole,
// never merges, and is sent back if any of its members would land on somebody else. the verdict
// maps every node involved to what it would see: the obstacles, the members of the group that
// would hit them, and the nodes those members move with, which are the ones to blame
const judge = (drag, nodes, followers, owners, editable) => {
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
    const group = members(drag, followers, owners)
    // the node each member moves with: a leader moves with itself, and a slot that follows a
    // factory moves with that factory
    const leaderOf = {}
    // go through the leaders
    for (const id of drag.group ?? [drag.id]) {
        // each leads itself
        leaderOf[id] = id
        // and the slots it takes along
        for (const follower of followers[id] ?? []) {
            // follow it
            leaderOf[follower] = id
        }
    }
    // the other members are slots that connect only to picked factories
    for (const id of group) {
        // each moves with the first of its factories, or by itself if it has none
        leaderOf[id] = leaderOf[id] ?? [...(owners[id] ?? [])][0] ?? id
    }
    // whoever, outside the group, sits at a spot
    const at = (x, y, z) => nodes.find(node => !group.has(node.id) && node.x === x && node.y === y && node.z === z)
    // how far the group moves
    const [dx, dy, dz] = [drag.tx - mover.x, drag.ty - mover.y, (drag.tz ?? mover.z) - mover.z]
    // the verdicts, by node
    const verdicts = {}
    // a move of the selection never merges, so every member is judged the same way, the mover
    // included; otherwise, the mover's landing is judged below
    const plain = drag.group !== undefined && drag.group !== null
    // go through the members
    for (const id of group) {
        // skipping the mover itself when its landing is judged below
        if (id === mover.id && !plain) {
            // on to the next
            continue
        }
        // the member
        const member = nodes.find(node => node.id === id)
        // whoever it would land on
        const other = member ? at(member.x + dx, member.y + dy, member.z + dz) : null
        // a member lands on somebody
        if (other) {
            // both of them see the collision
            verdicts[other.id] = "blocked"
            verdicts[member.id] = "blocked"
            // and so does the node it moves with, which is the one to blame
            verdicts[leaderOf[member.id]] = "blocked"
        }
    }
    // the node already where the mover is headed, if any, unless the mover was judged already
    const occupant = plain ? null : at(drag.tx, drag.ty, drag.tz ?? mover.z)
    // if there is one
    if (occupant) {
        // nothing merges on a diagram that cannot be edited; elsewhere, a factory on either side,
        // or two slots that both carry products, cannot share a spot
        const blocked = !editable || mover.kind === "factory" || occupant.kind === "factory"
            || (mover.bound && occupant.bound)
        // record what the occupant sees
        verdicts[occupant.id] = blocked ? "blocked" : "merge"
        // and, when it is sent back, so does the mover
        if (blocked) {
            // which is the one to blame
            verdicts[mover.id] = "blocked"
        }
    }
    // if anything is blocked, the whole move is sent back
    if (Object.values(verdicts).includes("blocked")) {
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
