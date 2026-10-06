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


// render a factory: read its state, and hand it to the drawing of the view in use
export const Factory = ({ factory }) => {
    // unpack
    const { id, at, inputs, outputs, family } = useFragment(factoryFlowDiagramFragment, factory)
    // get the current selection
    const { selection } = useSelection()
    // am i selected
    const selected = selection.includes(id)
    // the drawing of the view in use
    const { Factory: Glyph } = glyphs[useProjection().name]
    // render
    return (
        <Glyph id={id} at={at} family={family} inputs={inputs} outputs={outputs} selected={selected} />
    )
}


// my fragment
const factoryFlowDiagramFragment = graphql`
    fragment factoryFlowDiagramFragment on FlowFactory {
        # the id
        id
        # location
        at {
            x
            y
            z
        }
        # what it is
        family
        # number of inputs
        inputs
        # number of outputs
        outputs
    }
`


// end of file
