// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// construct the geometrical aspects of the controller
export const layout = ({
    // user coorsinate system
    min, max, major = [min, max],
    // viewport coordinates system
    width, height,
    // controller configuration
    direction = "row", labels = "bottom", arrow = "top",
}) => {
    // my cell size
    const cell = 10
    // the margin is the distance from the edge of the controller to the first/last major tick mark
    const margin = 4 * cell

    // directionality; borrow terms from flex
    const row = direction === "row"

    // the extents
    const extents = {
        "row": { main: width, cross: height, mainName: "width", crossName: "height" },
        "column": { main: height, cross: width, mainName: "height", crossName: "width" },
    }
    // deduce the main and cross axis extents
    const { main, cross, mainName, crossName } = extents[direction]

    // my cross size is precisely 10 cells
    const iCross = 10 * cell
    // and it sets my intrinsic length scale
    const ils = cross / iCross
    // my main size is now determined by my aspect ratio
    const iMain = main / ils

    // the transofrmation that scales the control
    const scale = `scale(${ils})`
    // the transofrmation that centers the control along the cross axis
    const center = row ? `translate(0 ${5 * cell})` : `translate(${5 * cell} 0)`
    // assemble the transofrm that places the control on the screen
    const place = `${scale} ${center}`
    // and express the bounding box in these coordinates
    const boundingBox = {
        x: row ? 0 : -5 * cell,
        y: row ? -5 * cell : 0,
        [mainName]: iMain,
        [crossName]: iCross,
    }

    // the scaling factor for projecting user values to diagram coordinates
    const userScale = (iMain - 2 * margin) / (max - min)
    // project a user value along the main axis
    const userToICS = value => {
        // clip
        value = Math.min(Math.max(value, min), max)
        // compute the offset in diagram coordinates and return it
        return margin + userScale * (value - min)
    }

    // the scaling factor for projecting viewport coordinates to user values
    const viewportScale = (max - min) / (iMain - 2 * margin)
    // project mouse coordinates to user values
    const mouseToUser = pixels => {
        // project
        const value = min + viewportScale * (pixels * ils - margin)
        // clip and return
        return Math.min(Math.max(value, min), max)
    }

    // my axis occupies the entire main extent
    const axis = row ? `M 0 0 l ${iMain} 0` : `M 0 0 l 0 ${iMain}`

    // generate the marker
    const marker = {
        top: `M 0 0 l ${-cell} ${-2 * cell} l ${2 * cell} 0 z`,
        bottom: `M 0 0 l ${-cell} ${2 * cell} l ${2 * cell} 0 z`,
        right: `M 0 0 l ${2 * cell} ${-cell} l 0 ${2 * cell} z`,
        left: `M 0 0 l ${-2 * cell} ${-cell} l 0 ${2 * cell} z`,
    }
    // and position it
    const markerPosition = {
        top: value => `translate(${userToICS(value)} ${-2.5 * cell})`,
        bottom: value => `translate(${userToICS(value)} ${2.5 * cell})`,
        right: value => `translate(${2.5 * cell} ${userToICS(value)})`,
        left: value => `translate(${-2.5 * cell} ${userToICS(value)})`,
    }

    // position a label at a given user value
    const labelPosition = {
        top: value => ({ x: userToICS(value), y: -2.5 * cell }),
        bottom: value => ({ x: userToICS(value), y: 4.5 * cell }),
        left: value => ({ x: -3 * cell, y: userToICS(value) + cell }),
        right: value => ({ x: 3 * cell, y: userToICS(value) + cell }),
    }

    // position a major tick mark
    const majorPosition = {
        "row": value => `M ${userToICS(value)} ${-cell} l 0 ${2 * cell}`,
        "column": value => `M ${-cell} ${userToICS(value)} l ${2 * cell} 0`,
    }

    // all done
    return {
        arrow,
        axis,
        boundingBox,
        cell,
        cross,
        crossName,
        direction,
        marker: marker[arrow],
        markerPosition: markerPosition[arrow],
        height,
        iCross,
        ils,
        iMain,
        labelPosition: labelPosition[labels],
        labels,
        main,
        mainName,
        major,
        majorPosition: majorPosition[direction],
        margin,
        max,
        min,
        mouseToUser,
        place,
        userScale,
        userToICS,
        viewportScale,
        width,
    }
}


// end of file
