// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useConfig } from "./useConfig"
import { useStartSliding } from './useStartSliding'


// render the value indicator
export const Marker = ({ value, id = 0, ...rest }) => {
    // make a handler that indicates the user is dragging the marker to pick a new value
    const startSliding = useStartSliding()

    // unpack the geometry
    const { enabled, marker, markerPosition } = useConfig()
    // pick a styling based on my state
    const Indicator = enabled ? Enabled : Disabled

    // make a handler to indicate the beginning of dragging the marker
    const start = evt => {
        // save the marker {id} and the current mouse position
        startSliding(id, evt)
        // all done
        return
    }
    // set up my event handlers
    const behaviors = enabled ? {
        // when the user clicks in my client area, start modifying the value
        onMouseDown: start,
    } : {}

    // render
    return (
        <g transform={markerPosition(value)} {...behaviors} >
            <Indicator d={marker} {...rest} />
        </g>
    )
}


// styling
// when disabled
const Disabled = styled.path`
    fill: ${props => theme.page.dim};
    stroke: ${props => theme.page.dim};
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
`


// when enabled
const Enabled = styled.path`
    & {
        fill: ${props => theme.page.normal};
        stroke: ${props => theme.page.normal};
        stroke-width: 2;
        vector-effect: non-scaling-stroke;
        cursor: pointer;
    }

    &:hover {
        fill: ${props => theme.page.highlight};
        stroke: ${props => theme.page.highlight};
    }

    &:active {
        fill: ${props => theme.page.highlight};
        stroke: ${props => theme.page.highlight};
    }
`


// end of file
