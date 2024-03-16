// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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


// draw an axis in the controller native coordinate system
export const Interval = ({ value, ...rest }) => {
    // make a handler that indicates the user is dragging the interval to pick a new range
    const startSliding = useStartSliding()

    // get the path generator
    const { enabled, intervalPosition } = useConfig()

    // form my path
    const path = intervalPosition(value)
    // pick a renderer
    const Path = enabled ? Enabled : Disabled

    // make a handler to indicate the beginning of dragging the marker
    const start = evt => {
        // indicate that both markers are sliding and record the current position of the mouse
        startSliding(-1, evt)
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
        <Path d={path} {...rest} {...behaviors} />
    )
}


// styling
const Base = styled.path`
    fill: none;
    stroke-width: 5;
    vector-effect: non-scaling-stroke;
`

const Disabled = styled(Base)`
    stroke: ${props => theme.page.dim};
`


const Enabled = styled(Base)`
    & {
        stroke: ${props => theme.page.normal};
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
