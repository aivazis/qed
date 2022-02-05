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
export const Indicator = ({ state, width, height }) => {

    // my path
    const path = `M 0 0 l -${width / 2} -${height} l ${width} 0 z`

    // extra paint for the highlighter
    const [polish, setPolish] = React.useState(false)

    // my controllers
    let behaviors = {
        // always remove the highlight
        onMouseLeave: () => setPolish(false),
    }

    // if i'm enabled
    if (state === "enabled") {
        // add the highlighter to my behaviors
        behaviors = {
            ...behaviors,
            // when the mouse enters my area
            onMouseEnter: () => setPolish(true),
        }
    }

    // mix my paint
    const paint = styles.indicator({ state, polish })

    // render
    return (
        <path d={path} {...behaviors} style={paint} />
    )
}


// end of file
