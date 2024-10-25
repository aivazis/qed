// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Connector } from './connector'


// render the connectors
export const Connectors = ({ diagram }) => {
    // if anything went wrong extracting the flow diagram
    if (!diagram) {
        // bail silently
        return
    }
    // extract the connectors
    const { connectors } = useFragment(connectorsFlowDiagramFragment, diagram)
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
