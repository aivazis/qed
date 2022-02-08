// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import { useGetZoomLevel } from "../viz/useGetZoomLevel"
import { useSetZoomLevel } from "../viz/useSetZoomLevel"

// locals
// styles
import styles from './styles'


// zoom level labels
export const Label = ({ value, state, geometry }) => {
    // look up the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // and grab the zoom level mutator
    const setZoom = useSetZoomLevel()

    // unpack my geometry
    const { labelPosition } = geometry
    // and compute my location
    const { x, y } = labelPosition(value)

    // extra paint for the highlighter
    const [polish, setPolish] = React.useState(false)

    // check whether i'm the current value
    if (state === "enabled" && zoom === value) {
        // and if so, upgrade my state
        state = "selected"
    }

    // my controllers
    let behaviors = {
        // turn the highlight off when the cursor leaves my area
        onMouseLeave: () => setPolish(false),
    }

    // if i'm enabled
    if (state === "enabled") {
        // add the highlighter to my behaviors
        behaviors = {
            ...behaviors,
            // when the cursor enters my area
            onMouseEnter: () => setPolish(true),
            // when the user clicks me
            onClick: () => setZoom(value)
        }
    }

    // mix my paint
    const paint = styles.label({ state, polish })

    // render
    return (
        <text x={x} y={y} {...behaviors} style={paint}>
            {value}
        </text>
    )
}


// end of file
