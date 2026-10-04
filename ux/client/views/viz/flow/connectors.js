// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Connector } from './connector'


// render the connectors
export const Connectors = ({ diagram }) => {
    // extract the connectors
    const data = useFragment(connectorsFlowDiagramFragment, diagram)
    // if anything went wrong extracting the flow diagram
    if (!data) {
        // bail silently
        return null
    }
    // otherwise, unpack the connectors
    const { connectors } = data
    // render
    return (
        <>
            {connectors.map(connector => (<Connector key={connector.id} connector={connector} />))}
        </>
    )
}

// my fragment
const connectorsFlowDiagramFragment = graphql`
    fragment connectorsFlowDiagramFragment on FlowDiagram {
        connectors {
            # the ids
            id
            # plus whatever the connector renderer needs
            ...connectorFlowDiagramFragment
        }
    }
`


// end of file
