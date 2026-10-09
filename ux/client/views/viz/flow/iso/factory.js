// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the paint of the plexes and the terminals
import plexPaint from '~/shapes/plex/styles'
import terminalPaint from '~/shapes/terminal/styles'

// local
// the projection
import { useProjection } from '../projection'
// components
import { Node } from '../node'
import { FloorPlex, FloorTerminal, PUCK_HEIGHT, Puck } from './solids'
// paint
import styles from '../styles'


// a factory seen from the side: its plexes on the floor along its x axis, and a puck painted by
// how far down it is pinned
export const IsoFactory = ({ id, at, family, level, inputs, outputs, selected }) => {
    // the projection
    const { project, view, labelLift } = useProjection()
    // the leader rises from the top of my puck to just under my name, which floats above me
    const [rise, name] = [view({ x: 0, y: 0, z: PUCK_HEIGHT }), view({ x: 0, y: 0, z: labelLift("factory") - 0.25 })]
    // the plexes sit a cell away along the x axis of the factory, on the floor
    const cell = 2
    const [west, east] = [project({ x: -cell, y: 0, z: 0 }), project({ x: cell, y: 0, z: 0 })]
    // an end with slots gets a plex, one without gets a terminal
    const end = slots => slots
        ? <FloorPlex paint={plexPaint} />
        : <FloorTerminal paint={terminalPaint} />
    // render
    return (
        <Node
            id={id} kind="factory" position={at}
            handles={{ "data-qed-family": family, "data-qed-level": level }}
        >
            {/* the axis that joins the plexes */}
            <line x1={west.x} y1={west.y} x2={east.x} y2={east.y} style={styles.connector} />
            {/* the plexes where the slots connect, or terminals at an end without slots, lying
                on the floor */}
            <g transform={`translate(${west.x} ${west.y})`}>{end(inputs)}</g>
            <g transform={`translate(${east.x} ${east.y})`}>{end(outputs)}</g>
            {/* the puck, in the color of factories, painted by how far down i am pinned */}
            <Puck highlight={selected} paint={styles.isoLevels.factory[level] ?? styles.iso.factory} />
            {/* the leader up to my name */}
            <line x1={rise.x} y1={rise.y} x2={name.x} y2={name.y} style={styles.iso.leader} />
        </Node>
    )
}


// end of file
