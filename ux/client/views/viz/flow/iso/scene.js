// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// the projection
import { useProjection } from '../projection'
// components
import { Connectors } from '../connectors'
import { Factory } from '../factory'
import { Labels } from '../labels'
import { Slot } from '../slot'
import { Cell, Floor } from './floor'


// a diagram seen from the side: the floor under its {nodes}, the cell under the pointer, the
// connectors, the factories and slots as one list ordered by how near each is to the viewer, so
// the nearer ones are drawn over the farther ones whatever their kind, and the labels over all
export const IsoScene = ({ diagram, nodes }) => {
    // extract the nodes
    const data = useFragment(sceneFlowDiagramFragment, diagram)
    // the projection, which knows how near a point is
    const { depth } = useProjection()
    // if anything went wrong extracting the diagram
    if (!data) {
        // bail silently
        return null
    }
    // otherwise, tag the factories and slots with their kind
    const solids = [
        ...data.factories.map(node => ({ kind: "factory", node })),
        ...data.slots.map(node => ({ kind: "slot", node })),
    ]
    // and order them, the farthest first
    solids.sort((a, b) => depth(a.node.at) - depth(b.node.at))
    // render
    return (
        <>
            <Floor nodes={nodes} />
            <Cell />
            <Connectors diagram={diagram} />
            {solids.map(({ kind, node }) => kind === "factory"
                ? <Factory key={node.id} factory={node} />
                : <Slot key={node.id} slot={node} />)}
            <Labels diagram={diagram} />
        </>
    )
}


// my fragment
const sceneFlowDiagramFragment = graphql`
    fragment sceneFlowDiagramFragment on FlowDiagram {
        factories {
            id
            # where it is, to tell how near it is
            at {
                x
                y
                z
            }
            # plus whatever the factory renderer needs
            ...factoryFlowDiagramFragment
        }
        slots {
            id
            # where it is, to tell how near it is
            at {
                x
                y
                z
            }
            # plus whatever the slot renderer needs
            ...slotFlowDiagramFragment
        }
    }
`


// end of file
