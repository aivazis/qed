// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the camera, which knows where the pointer is
import { useCamera } from '~/widgets/camera'

// local
// the projection
import { useProjection } from '../projection'
// paint
import styles from '../styles'


// the lattice of the floor under the {nodes} of a diagram, a cell wide, with room to spare
export const Floor = ({ nodes, margin = 6 }) => {
    // the projection
    const { project } = useProjection()
    // a diagram without nodes
    if (nodes.length === 0) {
        // has no floor to show
        return null
    }
    // snap a coordinate to the cells, in the given direction
    const snap = (value, direction) => 2 * Math[direction](value / 2)
    // the extent of the nodes, padded and snapped to the cells
    const xs = nodes.map(node => node.x)
    const ys = nodes.map(node => node.y)
    const [x0, x1] = [snap(Math.min(...xs) - margin, "floor"), snap(Math.max(...xs) + margin, "ceil")]
    const [y0, y1] = [snap(Math.min(...ys) - margin, "floor"), snap(Math.max(...ys) + margin, "ceil")]
    // the lines, as segments from one end to the other
    const segments = []
    // the ones along y, one per cell along x
    for (let x = x0; x <= x1; x += 2) {
        // from end to end
        segments.push([project({ x, y: y0, z: 0 }), project({ x, y: y1, z: 0 })])
    }
    // the ones along x, one per cell along y
    for (let y = y0; y <= y1; y += 2) {
        // from end to end
        segments.push([project({ x: x0, y, z: 0 }), project({ x: x1, y, z: 0 })])
    }
    // as one path
    const path = segments.map(([a, b]) => `M ${a.x} ${a.y} L ${b.x} ${b.y}`).join(" ")
    // render
    return (
        <path d={path} style={styles.iso.floor} data-qed-floor />
    )
}


// the cells of the floor around the grid point under the pointer
export const Cell = () => {
    // the pointer, before it is rounded onto the grid
    const { pointer } = useCamera()
    // the projection
    const { project, ground } = useProjection()
    // without a pointer
    if (pointer === null) {
        // there is nothing to mark
        return null
    }
    // map the pointer onto the floor
    const { dx, dy } = ground({ dx: pointer.x, dy: pointer.y })
    // the nearest grid point
    const [gx, gy] = [Math.round(dx), Math.round(dy)]
    // the corners of the cells around it, on the screen
    const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        .map(([cx, cy]) => project({ x: gx + cx, y: gy + cy, z: 0 }))
        .map(({ x, y }) => `${x},${y}`).join(" ")
    // mark them
    return (
        <polygon points={corners} style={styles.iso.cell} data-qed-cursor={`${gx},${gy}`} />
    )
}


// end of file
