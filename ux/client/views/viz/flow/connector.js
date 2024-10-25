// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// paint
import styles from './styles'


// render a connector
export const Connector = ({ connector, style }) => {
    // unpack
    const { input, factory, slot } = useFragment(connectorFlowDiagramFragment, connector)

    // distinguish between input and output connectors
    const delta = 2 * (input ? -1 : 1)
    // compute the connector path
    const path = `
        M ${factory.x + delta} ${factory.y}
        L ${slot.x - delta} ${slot.y}
        L ${slot.x} ${slot.y}
    `
    // mix the paint
    const paint = { ...styles.connector, ...style }
    // render
    return (
        <path d={path} style={paint} />
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
    }
`

// end of file
