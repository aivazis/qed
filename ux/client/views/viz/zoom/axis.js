// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// styles
import styles from './styles'


// the x axis
export const Axis = ({ geometry }) => {
    // unpack my geometry
    const { axis } = geometry
    // my path
    const path = `M 0 0 l ${axis} 0`

    // get my paint
    const paint = styles.axis
    // and render
    return (
        <path d={path} style={paint} />
    )
}


// end of file
