// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// the diagram on the canvas
import { useDiagram } from './diagram'


// move a node of the pipeline diagram on the canvas
export const useMoveNode = () => {
    // the diagram
    const { id: diagram } = useDiagram()
    // moving a node mutates the server side diagram
    const [commit, pending] = useMutation(useMoveNodeMutation)
    // and so does moving the selection
    const [commitGroup, pendingGroup] = useMutation(useMoveNodeGroupMutation)
    // the steps of a live drag fire far faster than the server round trip, so at most one is in
    // flight and, while it is, only the LATEST is remembered; the drop ends the drag, so a step
    // still waiting when it happens is dropped, lest it pick the node back up after it landed
    const inflight = React.useRef(false)
    const queued = React.useRef(null)
    // the landing, when it arrives while a step is in flight; it waits for the step, since two
    // requests in flight need not reach the server in the order they were sent
    const landing = React.useRef(null)
    // send one request
    const send = ({ id, x, y, z, group = null }, settled, done) => {
        // the selection moves as a whole, led by the dragged node, and leaves nothing behind to
        // settle; a node on its own moves by itself
        const [mutate, input] = group !== null
            ? [commitGroup, { diagram, nodes: group, anchor: id, x, y, z }]
            : [commit, { diagram, node: id, x, y, z, settled }]
        // send it
        mutate({
            // the payload
            variables: { input },
            // when it lands, the diagram in the response replaces the one on screen
            onCompleted: () => done(),
            // on failure, report, and still let the caller settle
            onError: errors => {
                // show me
                console.log(`viz.flow.useMoveNode:`)
                console.group()
                console.log(`ERROR while moving node ${id} to (${x}, ${y}, ${z})`)
                console.log(errors)
                console.groupEnd()
                // settle
                done()
            },
        })
        // all done
        return
    }
    // a step of a drag in progress: send it now if the channel is free, otherwise hold only the
    // latest one until it is
    const step = target => {
        // if a step is in flight
        if (inflight.current) {
            // remember only the most recent one
            queued.current = target
            // and let the one in flight send it
            return
        }
        // otherwise, the channel is busy now
        inflight.current = true
        // send the step; when it settles, send whatever arrived in the meantime
        send(target, false, () => {
            // free again
            inflight.current = false
            // if the drag ended while the step was in flight
            if (landing.current !== null) {
                // unpack the landing
                const { target, done } = landing.current
                // it is no longer waiting
                landing.current = null
                // send it
                send(target, true, done)
                // and that is the end of the drag
                return
            }
            // the latest step that arrived while busy, if any
            const next = queued.current
            // if there is one
            if (next !== null) {
                // consume it
                queued.current = null
                // and send it
                step(next)
            }
        })
        // all done
        return
    }
    // where the node lands; {done} runs once the server has answered, either way
    const move = (target, done = () => { }) => {
        // the drag is over, so a step still waiting is moot
        queued.current = null
        // if a step is in flight
        if (inflight.current) {
            // the landing waits for it
            landing.current = { target, done }
            // all done
            return
        }
        // otherwise, send the landing
        send(target, true, done)
        // all done
        return
    }
    // publish
    return { move, step, pending: pending || pendingGroup }
}


// the mutation; the response carries the whole diagram, since dropping a slot on another merges
// the two, which adds and removes nodes, labels, and connectors
const useMoveNodeMutation = graphql`
    mutation useMoveNodeMutation($input: DiagramMoveInput!) {
        diagramMove(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

// the mutation that moves the selection, which carries the whole diagram back as well
const useMoveNodeGroupMutation = graphql`
    mutation useMoveNodeGroupMutation($input: DiagramMoveGroupInput!) {
        diagramMoveGroup(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

// end of file
