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
    // the two ends, where they are now
    const [fx, fy] = [factory.x + fs.dx, factory.y + fs.dy]
    const [sx, sy] = [slot.x + ss.dx, slot.y + ss.dy]

    // distinguish between input and output connectors
    const delta = 2 * (input ? -1 : 1)
    // compute the connector path
    const path = `
        M ${fx + delta} ${fy}
        L ${sx - delta} ${sy}
        L ${sx} ${sy}
    `
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
        }
        slot {
            x
            y
        }
        # the nodes at my ends, so i can follow them while they are dragged
        factoryId
        slotId
    }
`


// end of file
