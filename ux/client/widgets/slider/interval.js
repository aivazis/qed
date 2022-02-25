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


// draw an axis in the controller native coordinate system
export const Interval = ({ value, enabled, ...rest }) => {
    // get the path generator
    const { intervalPosition } = useConfig()

    // form my path
    const path = intervalPosition(value)
    // pick a renderer
    const Path = enabled ? Enabled : Disabled

    // render
    return (
        <Path d={path} {...rest} />
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
