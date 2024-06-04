// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a scale and orientation indicator
export const Compass = ({ style, ...xforms }) => {
    // mix paint
    // for my container
    const boxStyle = { ...styles.box, ...style?.box }
    // for the axis markers
    const eStyle = { ...styles.east, ...style?.east }
    const nStyle = { ...styles.north, ...style?.north }
    // for the compass face
    const faceStyle = { ...styles.face, ...style?.face }
    // and the needle
    const needleStyle = { ...styles.needle, ...style?.needle }

    return (
        <g {...boxStyle} {...xforms}>
            {/* the x-axis */}
            <line x1="-0.5" y1="0" x2="0.5" y2="0" {...eStyle} />
            {/* the y-axis */}
            <line x1="0" y1="-0.5" x2="0" y2="0.5" {...nStyle} />

            {/* the inner marker */}
            <circle cx="0" cy="0" r=".1" {...faceStyle} />

            {/* the x-axis marker */}
            <path d="M -0.14142 0.14142
                    C 0 .25 0 .25 0.14142 0.14142
                    L 0 .3
                    Z"
                {...needleStyle} />
            {/* the y-axis marker */}
            <path d="M 0.14142 -0.14142
                    C .3 0 .3 0 0.14142 0.14142
                    L .3 0
                    Z"
                {...needleStyle} />
        </g>
    )
}


// end of file
