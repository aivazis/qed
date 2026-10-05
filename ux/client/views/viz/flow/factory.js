// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shape
import { Factory as Shape, Plex, Terminal } from '~/shapes'

// local
// hooks
import { useSelection } from './useSelection'
// components
import { Node } from './node'
// styles
import styles from './styles'


// render a factory
export const Factory = ({ factory }) => {
    // unpack
    const { id, at, inputs, outputs, family } = useFragment(factoryFlowDiagramFragment, factory)

    // get the current selection
    const { selection } = useSelection()
    // am i selected
    const selected = selection.includes(id)

    // make a wide factory
    const cell = 2
    // prerender the input terminal
    const inplex = (
        <g transform={`translate(${-cell} 0)`}>
            {inputs ? <Plex /> : <Terminal />}
        </g>
    )
    // the output terminal
    const outplex = (
        <g transform={`translate(${cell} 0)`}>
            {outputs ? <Plex /> : <Terminal />}
        </g>
    )
    // assemble the graphic and render it
    return (
        <Node id={id} kind="factory" position={at} handles={{ "data-qed-family": family }}>
            <Shape highlight={selected} cell={cell} style={styles} />
            {inplex}
            {outplex}
        </Node>
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
