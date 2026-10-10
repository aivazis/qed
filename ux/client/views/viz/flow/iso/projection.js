// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the isometric axes, before any turn: the diagram x axis runs down and to the right, its y axis
// down and to the left, both at thirty degrees from the horizontal, and its z axis straight up
const C = Math.cos(Math.PI / 6)
const S = Math.sin(Math.PI / 6)
// the height of a unit along z, on the screen
const H = 1


// build the isometric projection {spec} asks for, which can be turned around the vertical axis
// by a number of quarter turns, {azimuth}, and seen from {below} the floor
export const makeIso = (spec = {}) => {
    // unpack the settings
    const { azimuth = 0, below = false } = spec
    // the quarter turns, in [0, 4)
    const turns = ((azimuth % 4) + 4) % 4
    // turn a point of the floor by that many quarter turns
    const rotate = ({ x, y }) => [[x, y], [y, -x], [-x, -y], [-y, x]][turns]
    // seen from below, the floor tilts the other way; up stays up
    const tilt = below ? -1 : 1
    // where a point lands, once turned
    const view = ({ x, y, z = 0 }) => ({ x: (x - y) * C, y: tilt * (x + y) * S - z * H })
    // where a point lands
    const project = point => {
        // turn it
        const [x, y] = rotate(point)
        // and place it
        return view({ x, y, z: point.z ?? 0 })
    }
    // where the unit steps along the floor land, which is all it takes to undo the projection
    // of a displacement on the floor
    const [ex, ey] = [project({ x: 1, y: 0, z: 0 }), project({ x: 0, y: 1, z: 0 })]
    const det = ex.x * ey.y - ey.x * ex.y
    // the displacement on the floor that moves a point by {dx, dy} on the screen
    const ground = ({ dx, dy }) => ({
        dx: (ey.y * dx - ey.x * dy) / det,
        dy: (ex.x * dy - ex.y * dx) / det,
    })
    // the change of height that moves a point by {dy} on the screen
    const lift = dy => -dy / H
    // how near a point is to the viewer: further along the turned floor, and higher when seen
    // from above or lower when seen from below; nearer points are drawn later
    const depth = point => {
        // turn it
        const [x, y] = rotate(point)
        // and measure it
        return x + y + tilt * (point.z ?? 0)
    }
    // the name of a factory floats above its puck
    const labelLift = category => category === "factory" ? 2.5 : 0
    // assemble
    return {
        name: "iso", key: `iso:${turns}:${below}`,
        below,
        project, view, ground, lift, depth, labelLift,
    }
}


// end of file
