// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// the control geometry
export const dimensions = ({ min = 0, max = 4, ticks = max - min + 1, height, width }) => {
    // the cell size
    const cell = 10
    // record the number of ticks
    const major = ticks

    // my height is exactly 10 cells, so the height in page coordinates determines the  conversion
    // to my intrinsic length scale
    const ils = height / (10 * cell) // page pixels per unit
    // the axis occupies the entire width of the control
    const axis = width / ils

    // figure out the spacing
    const spacing = axis / major
    // leave a margin of half a spacing on each side
    const margin = spacing / 2

    // compute the diagram coordinate of a user value; clip if out of bounds
    const userToICS = value => {
        // clip
        value = Math.min(Math.max(value, min), max)
        // compute the offset in diagram coordinates and return it
        return margin + (value - min) * spacing
    }

    // convert mouse coordinates to user values
    const viewportToUser = x => Math.max(Math.min((x / ils - margin) / spacing, max), min)

    // position a tick at a given value
    const majorTickPosition = value => ({
        // the coordinates of its tip
        x: userToICS(value),
        y: -cell,
    })

    const majorTickLength = 2 * cell

    // position a label at a given value
    const labelPosition = value => ({
        // the coordinates of the anchor
        x: userToICS(value),
        y: 4.5 * cell,
    })

    // the indicator
    const indicator = `M 0 0 l ${-cell} ${-2 * cell} l ${2 * cell} 0 z`
    // position the indicator at a given value
    const indicatorPosition = value => ({
        // the coordinates of the tip
        x: userToICS(value),
        y: -2.5 * cell,
    })

    // make available
    return {
        axis,
        cell,
        indicator,
        indicatorPosition,
        height,
        ils,
        labelPosition,
        major,
        majorTickLength,
        majorTickPosition,
        margin,
        max,
        min,
        spacing,
        userToICS,
        viewportToUser,
        width,
    }
}


// end of file
