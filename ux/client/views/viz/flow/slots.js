// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Slot } from './slot'


// render the slots
export const Slots = ({ diagram }) => {
    // if anything went wrong extracting the flow diagram
    if (!diagram) {
        // bail silently
        return
    }
    // extract the list of slots
    const { slots } = useFragment(slotsFlowDiagramFragment, diagram)
    // render
    return (
        <>
            {slots.map(slot => (<Slot key={slot.id} slot={slot} />))}
        </>
    )
}

// my fragment
const slotsFlowDiagramFragment = graphql`
    fragment slotsFlowDiagramFragment on FlowDiagram {
        slots {
            # the ids
            id
            # plus whatever the slot renderer needs
            ...slotFlowDiagramFragment
        }
    }
`


// end of file
