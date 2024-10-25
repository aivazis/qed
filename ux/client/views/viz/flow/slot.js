// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shape
import { Slot as Unbound } from '~/shapes'
import { Product as Bound } from '~/shapes'

// local
// components
import { Node } from './node'


// render a slot
export const Slot = ({ slot }) => {
    // unpack
    const { id, at, bound } = useFragment(slotFlowDiagramFragment, slot)

    // get the current selection
    // MGA - FIXME: enabled node selection
    // const { selection } = useSelection()
    const { selection } = { selection: [] }
    // am i selected
    const selected = selection.includes(id)

    // decide what kind of slot to render
    const Slot = bound ? Bound : Unbound
    // assemble the graphic and render it
    return (
        <Node id={id} position={at}>
            <Slot highlight={selected} />
        </Node>
    )
}


// my fragment
const slotFlowDiagramFragment = graphql`
    fragment slotFlowDiagramFragment on FlowSlot {
        # the id
        id
        # location
        at {
            x
            y
        }
        # state
        bound
    }
`

// end of file
