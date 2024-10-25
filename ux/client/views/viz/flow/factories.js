// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Factory } from './factory'


// render the factory nodes
export const Factories = ({ diagram }) => {
    // if anything went wrong extracting the flow diagram
    if (!diagram) {
        // bail silently
        return
    }
    // extract the list of factories
    const { factories } = useFragment(factoriesFlowDiagramFragment, diagram)
    // render
    return (
        <>
            {factories.map(factory => (<Factory key={factory.id} factory={factory} />))}
        </>
    )
}

// my fragment
const factoriesFlowDiagramFragment = graphql`
    fragment factoriesFlowDiagramFragment on FlowDiagram {
        factories {
            # the ids
            id
            # plus whatever the factory renderer needs
            ...factoryFlowDiagramFragment
        }
    }
`


// end of file
