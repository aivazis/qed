// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// render the logo
export const QED = ({ style }) => {
    // paint me
    return (
        <g transform="rotate(-45 500 500)">
            <text x={500} y={700} style={styles.logo}>οεδ</text>
        </g>
    )
}


// end of file
