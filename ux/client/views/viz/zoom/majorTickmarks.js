// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// styles
import styles from './styles'


// the tick marks
export const MajorTickmarks = ({ geometry }) => {
    // unpack the control geometry
    const { min, major, majorTickLength, majorTickPosition } = geometry

    // compute the coordinates of the tick marks
    const ticks = new Array(major).fill(null).map((_, idx) => {
        // get the tips
        const { x, y } = majorTickPosition(min + idx)
        // form the path and return it
        return `M ${x} ${y} l 0 ${majorTickLength}`
    })


    // mix my paint
    const paint = styles.majorTickmark
    // render
    return (
        <path d={ticks.join(' ')} style={paint} />
    )
}


// end of file
