// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// components
import { Indicator } from "./indicator"
import { Legend } from "./legend"
// styles
import styles from './styles'


// the zoom controller
export const Controller = () => {
    // the zoom level
    const zoom = 0

    // pick a number of ticks
    const ticks = 5

    // set up a scale
    const width = 1000
    const height = width / 2

    // set a margin
    const margin = width / 10
    // figure out the spacing among tick marks
    const spacing = (width - 2 * margin) / (ticks - 1)

    // the indicator {x} coordinate is tied to the {zoom} level
    const x = margin + zoom * spacing
    // the indicator {y} coordinate is fixed
    const y = height / 2 - height / 8

    // render
    return (
        <>
            {/* the static background */}
            <Legend ticks={ticks}
                width={width} height={height} margin={margin} spacing={spacing} />
            {/* the movable value indicator */}
            <g transform={`translate(${x} ${y})`}>
                <Indicator width={75} height={60} />
            </g>
        </>
    )
}


// end of file
