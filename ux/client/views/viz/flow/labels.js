// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Label } from './label'


// render the labels
export const Labels = ({ diagram }) => {
    // if anything went wrong extracting the flow diagram
    if (!diagram) {
        // bail silently
        return
    }
    // extract the labels
    const { labels } = useFragment(labelsFlowDiagramFragment, diagram)
    // render
    return (
        <>
            {labels.map(label => (<Label key={label.id} label={label} />))}
        </>
    )
}

// my fragment
const labelsFlowDiagramFragment = graphql`
    fragment labelsFlowDiagramFragment on FlowDiagram {
        labels {
            # the ids
            id
            # plus whatever the label renderer needs
            ...labelFlowDiagramFragment
        }
    }
`


// end of file
