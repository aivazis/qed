// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the shapes the diagram draws factories with
import { Factory, Plex, Slot, Terminal } from '~/shapes'
// the paint of the diagram
import diagram from '../flow/styles'


// a factory drawn the way the diagram draws it, small: its body, its hub, and its slots fanned out
// on either side, connected the way the diagram connects them; {inputs} and {outputs} are the names
// of its slots, and {scale} is the size of a diagram unit in pixels
export const Miniature = React.forwardRef(({ inputs, outputs, scale = 5 }, ref) => {
    // the vertical places of {count} slots, the way the diagram spreads them around the hub
    const places = count => Array.from({ length: count }, (_, idx) => 2 * (2 * idx + 1 - count))
    // the slots on either side
    const left = places(inputs.length)
    const right = places(outputs.length)
    // the tallest side sets the height; the body above the hub sets a floor
    const reach = Math.max(left.length, right.length, 1)
    const top = Math.min(-2 * (reach - 1) - 0.75, -2.25)
    const bottom = Math.max(2 * (reach - 1) + 0.75, 0.75)
    // the box around it all, with the slots on the edges
    const [x0, width] = [-5.75, 11.5]
    const height = bottom - top
    // a connector, the way the diagram draws one: from the plex next to the hub, toward the slot
    const path = (side, y) => `M ${2 * side} 0 L ${3 * side} ${y} L ${5 * side} ${y}`
    // render
    return (
        <svg ref={ref} width={width * scale} height={height * scale}
            viewBox={`${x0} ${top} ${width} ${height}`} data-qed-miniature>
            {/* the connectors */}
            {left.map(y => <path key={`in:${y}`} d={path(-1, y)} style={diagram.connector} />)}
            {right.map(y => <path key={`out:${y}`} d={path(1, y)} style={diagram.connector} />)}
            {/* the slots */}
            {left.map(y => <g key={`slot:in:${y}`} transform={`translate(-5 ${y})`}><Slot /></g>)}
            {right.map(y => <g key={`slot:out:${y}`} transform={`translate(5 ${y})`}><Slot /></g>)}
            {/* the body and the hub */}
            <Factory cell={2} style={diagram} />
            {/* the plexes, or a terminal on a side without slots */}
            <g transform="translate(-2 0)">{left.length ? <Plex /> : <Terminal />}</g>
            <g transform="translate(2 0)">{right.length ? <Plex /> : <Terminal />}</g>
        </svg>
    )
})


// end of file
