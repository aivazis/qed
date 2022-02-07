// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
import { Label } from "./label"
// styles
import styles from './styles'


// the legend of the zoom controller
// by default, it is drawn in a (1000, 500) box
export const Legend = ({ state, ticks, width, height, margin, spacing }) => {
    // the height of the tick marks
    const dy = height / 10

    // compute the x coordinates of the tick marks
    const xTicks = new Array(ticks).fill(0).map((_, idx) => margin + idx * spacing)
    // the y coordinates are all fixed
    const yTicks = height / 2 - dy / 2

    // the y coordinates for the labels
    const yLabels = height / 2 + height / 5

    // mix my paint
    const paint = styles.controller
    // render
    return (
        <>
            {xTicks.map((x, value) => (
                <g key={value}>
                    {/* the tick mark */}
                    <path d={`M ${x} ${yTicks} l 0 ${dy}`} style={paint.tick} />
                    {/* the label */}
                    <Label state={state} value={value} x={x} y={yLabels} />
                </g>
            ))}
            <path key="axis" d={`M 0 ${height / 2} l ${width} 0`} style={paint.axis} />
        </>
    )
}


// end of file
