// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// local
// hooks
import { useConfig } from "./useConfig"
import { useStartSliding } from './useStartSliding'


// draw an axis in the controller native coordinate system
export const Interval = ({ value, enabled, ...rest }) => {
    // make a handler that indicates the user is dragging the interval to pick a new range
    const startSliding = useStartSliding()

    // get the path generator
    const { intervalPosition } = useConfig()

    // form my path
    const path = intervalPosition(value)
    // pick a renderer
    const Path = enabled ? Enabled : Disabled

    // set up my event handlers
    const behaviors = enabled ? {
        // when the user clicks in my client area, start modifying the value
        onMouseDown: () => startSliding(-1)
    } : {}


    // render
    return (
        <Path d={path} {...rest} {...behaviors} />
    )
}


// styling
const Base = styled.path`
    fill: none;
    vector-effect: non-scaling-stroke;
`

const Disabled = styled(Base)`
    stroke: none;
`


const Enabled = styled(Base)`
    stroke: hsl(28deg, 90%, 35%);
    stroke-width: 5;
`


// end of file
