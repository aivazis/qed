// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// hooks
import { useProjection } from './projection'
import { useSelection } from './useSelection'
// the drawings of each view
import { glyphs } from './glyphs'


// render a slot: read its state, and hand it to the drawing of the view in use
export const Slot = ({ slot }) => {
    // unpack
    const { id, at, bound, level } = useFragment(slotFlowDiagramFragment, slot)
    // get the current selection
    const { selection } = useSelection()
    // am i selected
    const selected = selection.includes(id)
    // the drawing of the view in use
    const { Slot: Glyph } = glyphs[useProjection().name]
    // render
    return (
        <Glyph id={id} at={at} bound={bound} level={level} selected={selected} />
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
            z
        }
        # state
        bound
        # how far down its product is pinned
        level
    }
`


// end of file
