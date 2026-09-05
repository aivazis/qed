// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the shape: a terminal, drawn as a frame with a prompt and a cursor
export const Console = ({ style }) => {
    // mix my paint
    const paint = styles.console(style)

    // paint me
    return (
        <>
            {/* the frame */}
            <rect x="100" y="180" width="800" height="640" rx="60" ry="60" style={paint.icon} />
            {/* the prompt */}
            <path d="M 260 340 L 440 500 L 260 660" style={paint.decoration} />
            {/* the cursor */}
            <line x1="520" y1="660" x2="740" y2="660" style={paint.decoration} />
        </>
    )
}


// end of file
