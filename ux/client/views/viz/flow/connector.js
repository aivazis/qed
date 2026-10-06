// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// the drag in progress
import { useDrag } from './drag'
// the projection
import { useProjection } from './projection'
// paint
import styles from './styles'


// render a connector
export const Connector = ({ connector, style }) => {
    // unpack
    const { id, input, factory, slot, factoryId, slotId } =
        useFragment(connectorFlowDiagramFragment, connector)
    // the drag in progress moves whichever end is attached to the node being dragged
    const { shiftOf } = useDrag()
    const fs = shiftOf(factoryId)
    const ss = shiftOf(slotId)
    // the projection
    const { project } = useProjection()
    // the two ends, where they are now
    const [fx, fy, fz] = [factory.x + fs.dx, factory.y + fs.dy, factory.z + fs.dz]
    const [sx, sy, sz] = [slot.x + ss.dx, slot.y + ss.dy, slot.z + ss.dz]

    // distinguish between input and output connectors
    const delta = 2 * (input ? -1 : 1)
    // the corners of the connector: the terminal of the factory, the point level with the slot,
    // and the slot itself
    const corners = [
        project({ x: fx + delta, y: fy, z: fz }),
        project({ x: sx - delta, y: sy, z: sz }),
        project({ x: sx, y: sy, z: sz }),
    ]
    // compute the connector path
    const path = corners.map(({ x, y }, i) => `${i ? "L" : "M"} ${x} ${y}`).join(" ")
    // mix the paint
    const paint = { ...styles.connector, ...style }
    // render
    return (
        <path d={path} style={paint}
            data-qed-connector={id} data-qed-factory={factoryId}
            data-qed-slot={slotId} data-qed-input={input} />
    )
}


// my fragment
const connectorFlowDiagramFragment = graphql`
    fragment connectorFlowDiagramFragment on FlowConnector {
        # the id
        id
        # state
        input
        factory {
            x
            y
            z
        }
        slot {
            x
            y
            z
        }
        # the nodes at my ends, so i can follow them while they are dragged
        factoryId
        slotId
    }
`


// end of file
