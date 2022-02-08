// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// hooks
import { useGetZoomLevel } from "../viz/useGetZoomLevel"
// styles
import styles from './styles'


// the zoom controller
export const Indicator = ({ geometry, state }) => {
    // the zoom level of the active viewport
    const zoom = useGetZoomLevel()

    // unpack my geometry
    const { indicator, indicatorPosition } = geometry
    // my position
    const { x, y } = indicatorPosition(zoom)

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
        <g transform={`translate( ${x} ${y})`}>
            <path d={indicator} {...behaviors} style={paint} />
        </g>
    )
}


// end of file
