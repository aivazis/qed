// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Factory } from '../factory'


// render the factory nodes
export const Factories = ({ diagram }) => {
    // extract the list of factories
    const data = useFragment(factoriesFlowDiagramFragment, diagram)
    // if anything went wrong extracting the flow diagram
    if (!data) {
        // bail silently
        return null
    }
    // otherwise, unpack the factories
    const { factories } = data
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
