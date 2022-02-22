// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// local
// hooks
import { useStartSliding } from './useStartSliding'


// render the value indicator
export const Marker = ({ value, geometry, enabled, ...rest }) => {
    // make a handler that indicates the user is dragging the marker to pick a new value
    const startSliding = useStartSliding()

    // unpack the geometry
    const { marker, markerPosition } = geometry
    // pick a styling based on my state
    const Indicator = enabled ? Enabled : Disabled

    // set up my event handlers
    const behaviors = enabled ? {
        // when the user clicks in my client area, start modifying the value
        onMouseDown: () => startSliding()
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
    fill: hsl(0deg, 0%, 20%);
    stroke: hsl(0deg, 0%, 20%);
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
`


// when enabled
const Enabled = styled.path`
    & {
        fill: hsl(0deg, 0%, 40%);
        stroke: hsl(0deg, 0%, 40%);
        stroke-width: 2;
        vector-effect: non-scaling-stroke;
        cursor: pointer;
    }

    &:hover {
        fill: hsl(28deg, 90%, 55%);
        stroke: hsl(28deg, 90%, 55%);
    }

    &:active {
        fill: hsl(28deg, 90%, 55%);
        stroke: hsl(28deg, 90%, 55%);
    }
`


// end of file
