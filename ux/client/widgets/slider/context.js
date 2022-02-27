// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// the provider factory
export const Provider = ({ config, children }) => {
    // a flag that indicates that the user has started dragging the marker
    // in order to support multiple movable markers, the state holds the marker id
    const [sliding, setSliding] = React.useState(null)

    // directional configuration
    const { direction, arrows, labels } = config
    // the layout of the controller in client coordinates
    const { height, width } = config
    // extract the controller limits and tick marks
    const { min, max, major } = config

    // my unit cell, in intrinsic coordinates
    const cell = 10
    // the margin is the distance from the edges to the outermost tick marks
    const margin = 4 * cell

    // table to help convert to flex terminology
    const extents = {
        row: {
            // extents in client coordinates
            mainClient: width,
            crossClient: height,
            // what to look up to provide extents
            mainName: "width",
            crossName: "height",
            // what to look up to form (x, y) pairs
            mainCoordinateName: "x",
            crossCoordinateName: "y",
            // mouse events
            mainMovementName: "movementX",
            crossMovementName: "movementY",
            mainOffsetName: "offsetX",
            crossOffsetName: "offsetY",
            // what to look up to extract dimensions from my client rectangle
            mainNearEdge: "left",
            // what to look to extract mouse coordinates from an event
            mainPosition: "clientX",
        },

        column: {
            // extents in client coordinates
            mainClient: height,
            crossClient: width,
            // what to look up to provide extents
            mainName: "height",
            crossName: "width",
            // what to look up to form (x, y) pairs
            mainCoordinateName: "y",
            crossCoordinateName: "x",
            // mouse events
            mainMovementName: "movementY",
            crossMovementName: "movementX",
            mainOffsetName: "offsetY",
            crossOffsetName: "offsetX",
            // what to look up to extract dimensions from my client rectangle
            mainNearEdge: "top",
            // what to look to extract mouse coordinates from an event
            mainPosition: "clientY",
        },
    }
    // decode and unpack
    const {
        mainClient, crossClient, mainName, crossName,
        mainCoordinateName, crossCoordinateName, mainNearEdge, mainPosition,
        mainMovementName, crossMovementName, mainOffsetName, crossOffsetName,
    } = extents[direction]

    // my cross axis is an integer number of cells
    const crossMine = 20 * cell
    // which sets my intrinsic length scale
    const ils = crossClient / crossMine // in client pixels / per intrinsic pixel
    // and the aspect ratio determines my main size
    const mainMine = mainClient / ils

    // my upper left hand corner, in my coordinate system
    const mainULMine = 0
    const crossULMine = - crossMine / 2
    // and my boundingBox as a rectangle {x,y, width,height}
    const bboxMine = {
        [mainCoordinateName]: mainULMine,
        [crossCoordinateName]: crossULMine,
        [mainName]: mainMine,
        [crossName]: crossMine,
    }

    // the transformation that scales the control and centers it along the cross axis
    const emplace = `scale(${ils}) translate(${-bboxMine.x} ${-bboxMine.y})`

    // the scaling factor for projecting user values to diagram coordinates
    const userScale = (mainMine - 2 * margin) / (max - min)
    // project a user value along the main axis
    const userToICS = value => {
        // clip
        value = Math.min(Math.max(value, min), max)
        // compute the offset in diagram coordinates and return it
        return margin + userScale * (value - min)
    }

    // the scaling factor for projecting viewport coordinates to user values
    const viewportScale = (max - min) / (mainMine - 2 * margin)
    // build a transform to project mouse coordinates to user values
    const mouseToUser = pixels => {
        // project
        const value = min + viewportScale * (pixels / ils - margin)
        // clip and return
        return Math.min(Math.max(value, min), max)
    }
    // project mouse motion to user coordinates
    const mouseDeltaToUser = delta => viewportScale * delta / ils

    // draw a line between two use values
    const intervalPosition = {
        row: interval => `M ${userToICS(interval[0])} 0 L ${userToICS(interval[1])} 0`,
        column: interval => `M 0 ${userToICS(interval[0])} L 0 ${userToICS(interval[1])}`,
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
        row: value => `M ${userToICS(value)} ${-cell} l 0 ${2 * cell}`,
        column: value => `M ${-cell} ${userToICS(value)} l ${2 * cell} 0`,
    }

    // generate the marker
    const marker = {
        top: `M 0 0 l ${-cell} ${-2 * cell} l ${2 * cell} 0 z`,
        bottom: `M 0 0 l ${-cell} ${2 * cell} l ${2 * cell} 0 z`,
        left: `M 0 0 l ${-2 * cell} ${-cell} l 0 ${2 * cell} z`,
        right: `M 0 0 l ${2 * cell} ${-cell} l 0 ${2 * cell} z`,
    }
    // and position it
    const markerPosition = {
        top: value => `translate(${userToICS(value)} ${-2.5 * cell})`,
        bottom: value => `translate(${userToICS(value)} ${2.5 * cell})`,
        left: value => `translate(${-2.5 * cell} ${userToICS(value)})`,
        right: value => `translate(${2.5 * cell} ${userToICS(value)})`,
    }

    // position a label at a given user value
    const markerLabelPosition = {
        top: value => ({ x: userToICS(value), y: -6 * cell }),
        bottom: value => ({ x: userToICS(value), y: 8.5 * cell }),
        left: value => ({ x: -5 * cell, y: userToICS(value) + cell }),
        right: value => ({ x: 5 * cell, y: userToICS(value) + cell }),
    }

    // build the initial context value
    const context = {
        // the sliding flag and its mutator
        sliding, setSliding,

        // directional configuration
        direction, arrows, labels,
        // the layout of the controller in client coordinates
        height, width,
        // the limits and tick marks
        min, max, major,

        // my unit cell
        cell,
        // my margin
        margin,

        // extents
        ils, mainMine, crossMine, bboxMine,
        // the transform that lets placemat put me on the screen
        emplace,
        // projection from mouse coordinates to user coordinates
        mouseToUser, mouseDeltaToUser,

        // layout
        intervalPosition: intervalPosition[direction],
        labelPosition: labelPosition[labels],
        majorPosition: majorPosition[direction],
        marker: marker[arrows],
        markerPosition: markerPosition[arrows],
        markerLabelPosition: markerLabelPosition[arrows],

        // names
        mainName, crossName, mainCoordinateName, crossCoordinateName,
        // mouse events
        mainMovementName, crossMovementName, mainOffsetName, crossOffsetName,
    }

    // provide from my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider>
    )
}


// set up the {zoom} context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // the sliding flag
        sliding: null,
        setSliding: () => { throw new Error(complaint) },

        // directional configuration
        direcion: null, arrows: null, labels: null,
        // the layout of the controller in client coordinates
        height: null, width: null,
        // the limits and tick marks
        min: null, max: null, major: null,

        // my unit cell
        cell: null,
        // my margin
        margin: null,
        // extents
        ils: null, mainMine: null, crossMine: null, ils: null,
        // the transform that lets placemat put me on the screen
        emplace: null,
        // projection from mouse coordinates to user coordinates
        mouseToUser: () => { throw new Error(complaint) },
        // names
        mainName: null, crossName: null, mainCoordinateName: null, crossCoordinateName: null,
        // mouse events
        mainMovementName: null, crossMovementName: null,
        mainOffsetName: null, crossOffsetName: null,
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'slider' context: no provider"


// end of file
