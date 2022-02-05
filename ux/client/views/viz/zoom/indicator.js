// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// styles
import styles from './styles'


// the zoom controller
export const Indicator = ({ width, height }) => {

    // my path
    const path = `M 0 0 l -${width / 2} -${height} l ${width} 0 z`

    // extra paint for the highlighter
    const [polish, setPolish] = React.useState(false)

    // my controllers
    const behaviors = {
        onMouseEnter: () => setPolish(true),
        onMouseLeave: () => setPolish(false),
    }

    // mix my paint
    const paint = styles.controller.indicator(polish)

    // render
    return (
        <path d={path} {...behaviors} style={paint} />
    )
}


// end of file
