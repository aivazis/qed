// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// the projection
import { useProjection } from '../projection'


// the height of the pucks, which the things drawn over them need to know
export const PUCK_HEIGHT = 0.3


// the points of a polygon through the projections of {corners}
const polygon = (corners, view) => corners.map(corner => {
    // project the corner
    const { x, y } = view(corner)
    // and format it
    return `${x},${y}`
}).join(" ")


// a plex, the spot where the slots of a factory connect to it, as a square lying on the floor,
// which the projection turns into a rhombus, like the cells of the floor
export const FloorPlex = ({ size = 0.125, paint }) => {
    // the projection
    const { view } = useProjection()
    // the corners of the square
    const corners = polygon([{ x: -size, y: -size }, { x: size, y: -size }, { x: size, y: size }, { x: -size, y: size }], view)
    // render
    return (
        <polygon points={corners} style={paint.icon} />
    )
}


// a terminal, the end of a factory that has no slots, as a circle with a cross lying on the floor
export const FloorTerminal = ({ radius = 0.5, arm = 0.2, paint }) => {
    // the projection
    const { view } = useProjection()
    // the circle projects onto an ellipse with these semi axes, whichever way the view is turned
    const [rx, ry] = [radius * Math.cos(Math.PI / 6) * Math.SQRT2, radius * 0.5 * Math.SQRT2]
    // the arms of the cross
    const [a, b, c, d] = [{ x: -arm, y: -arm }, { x: arm, y: arm }, { x: -arm, y: arm }, { x: arm, y: -arm }].map(view)
    // render
    return (
        <>
            <ellipse cx="0" cy="0" rx={rx} ry={ry} style={paint.decoration} />
            <path d={`M ${a.x} ${a.y} L ${b.x} ${b.y} M ${c.x} ${c.y} L ${d.x} ${d.y}`} style={paint.icon} />
        </>
    )
}


// a short cylinder that stands on the floor: its side, and its top, or its bottom when seen from
// below; slots and factories are both drawn as pucks
export const Puck = ({ highlight, radius = 0.5, height = PUCK_HEIGHT, paint }) => {
    // the projection
    const { view, below } = useProjection()
    // a circle on the floor projects onto an ellipse with these semi axes, whichever way the
    // view is turned
    const [rx, ry] = [radius * Math.cos(Math.PI / 6) * Math.SQRT2, radius * 0.5 * Math.SQRT2]
    // the height of the top, on the screen
    const top = view({ x: 0, y: 0, z: height }).y
    // the cap that faces the viewer, and the one hidden behind the side
    const [near, far] = below ? [0, top] : [top, 0]
    // render: the hidden cap and the band between the caps make the side
    return (
        <>
            <ellipse cx="0" cy={far} rx={rx} ry={ry} style={paint.side} />
            <rect x={-rx} y={top} width={2 * rx} height={-top} style={paint.band} />
            <ellipse cx="0" cy={near} rx={rx} ry={ry} style={paint.top} data-qed-grip />
            {highlight && <ellipse cx="0" cy={near} rx={rx * 1.5} ry={ry * 1.5} style={paint.highlight} />}
        </>
    )
}


// end of file
