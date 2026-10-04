// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
import { Slot } from './slot'


// render the slots
export const Slots = ({ diagram }) => {
    // extract the list of slots
    const data = useFragment(slotsFlowDiagramFragment, diagram)
    // if anything went wrong extracting the flow diagram
    if (!data) {
        // bail silently
        return null
    }
    // otherwise, unpack the slots
    const { slots } = data
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
