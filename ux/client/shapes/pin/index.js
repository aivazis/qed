// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the pin
const pin = `
M 747.4488 127.50676
C 681.32446 61.39885 593.472 25 499.96 25
C 406.488 25 318.59555 61.39885 252.5112 127.50676
C 186.40688 193.60468 150 281.4819 150 374.98895
C 150 438.18695 164.60875 491.1553 195.96606 541.6637
C 223.67369 586.2923 260.7805 623.1411 300.09713 662.1699
C 372.6209 734.1176 454.8139 815.705 489.84087 966.9103
C 490.9308 971.6501 495.1204 975 499.97 975
C 504.8296 975 509.0192 971.6501 510.11913 966.9103
C 545.1761 815.715 627.3791 734.1476 699.8629 662.1699
C 739.1995 623.1511 776.3163 586.2923 803.9939 541.6637
C 835.3713 491.1453 850 438.18695 850 374.98895
C 849.96 281.4819 813.5431 193.60468 747.4488 127.50676
Z
`

// render the shape
export const Pin = ({ style }) => {
    // mix my paint
    const paint = styles.pin(style)
    // and render
    return (
        <>
            <path d={pin} style={paint.icon} />
            <circle style={paint.decoration}
                cx="500" cy="400" r="150"
            />
        </>
    )
}


// end of file
