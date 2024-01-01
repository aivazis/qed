// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the shape
export const Live = ({ style }) => {
    // mix my paint
    const paint = styles.live(style)

    // paint me
    return (
        <>
            {/* the monitor */}
            <rect x="150" y="200" width="700" height="500" style={paint.icon} />
            <line x1="250" y1="800" x2="750" y2="800" style={paint.icon} />
            {/* the badge */}
            <circle cx="750" cy="750" r="200" style={paint.badge} />
            <path d="M 675 725 L 750 800 L 675 875" style={paint.decoration} />
            <path d="M 825 625 L 750 700 L 825 775" style={paint.decoration} />
        </>

    )
}


// end of file
