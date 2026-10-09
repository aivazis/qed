// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Factory as Shape, Plex, Terminal } from '~/shapes'

// local
// components
import { Node } from '../node'
// styles
import styles from '../styles'


// a factory seen from above: its shape, painted by how far down it is pinned, with a terminal a
// cell away on either side
export const FlatFactory = ({ id, at, family, level, inputs, outputs, selected }) => {
    // make a wide factory
    const cell = 2
    // paint it by how far down it is pinned
    const paint = { ...styles, icon: { ...styles.icon, ...styles.levels.factory[level]?.icon } }
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
        <Node
            id={id} kind="factory" position={at}
            handles={{ "data-qed-family": family, "data-qed-level": level }}
        >
            <Shape highlight={selected} cell={cell} style={paint} />
            {inplex}
            {outplex}
        </Node>
    )
}


// end of file
