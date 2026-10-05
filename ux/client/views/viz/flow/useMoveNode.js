// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// the active viewport, whose pipeline the diagram shows
import { useViewports } from '../viz/useViewports'


// move a node of the pipeline diagram of the active view
export const useMoveNode = () => {
    // the active viewport
    const { activeViewport } = useViewports()
    // moving a node mutates the server side diagram
    const [commit, pending] = useMutation(useMoveNodeMutation)
    // send a node to a new place; {done} runs once the server has answered, either way
    const move = ({ id, x, y, z }, done = () => { }) => {
        // send the request
        commit({
            // the payload
            variables: {
                input: { viewport: activeViewport, node: id, x, y, z },
            },
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
    // publish
    return { move, pending }
}


// the mutation; the response carries the whole diagram, since dropping a slot on another merges
// the two, which adds and removes nodes, labels, and connectors
const useMoveNodeMutation = graphql`
    mutation useMoveNodeMutation($input: ViewDiagramMoveInput!) {
        viewDiagramMove(input: $input) {
            diagram {
                id
                ...labelsFlowDiagramFragment
                ...connectorsFlowDiagramFragment
                ...slotsFlowDiagramFragment
                ...factoriesFlowDiagramFragment
                # the positions the camera centers on
                factories {
                    at {
                        x
                        y
                        z
                    }
                }
                slots {
                    at {
                        x
                        y
                        z
                    }
                }
            }
        }
    }
`

// end of file
