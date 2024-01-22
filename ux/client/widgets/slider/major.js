// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// local
// hooks
import { useConfig } from "./useConfig"


// render the major tick marks
export const Major = ({ ...rest }) => {
    // get the major tick mark values and the mark generator
    const { enabled, major, majorPosition } = useConfig()
    // render
    return (
        <g>
            {major.map(tick => {
                // pick an implementation based on my state
                const Path = enabled ? Enabled : Disabled
                // render
                return (
                    <Path key={tick} d={majorPosition(tick)} {...rest} />
                )
            })}
        </g>
    )
}


// styling
const Base = styled.path`
    fill: none;
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
`


const Disabled = styled(Base)`
    stroke: hsl(0deg, 0%, 20%);
`


const Enabled = styled(Base)`
    & {
        stroke: hsl(0deg, 0%, 40%);
    }

    &:hover {
        stroke: hsl(28deg, 90%, 55%);
    }

    &:active {
        stroke: hsl(28deg, 90%, 55%);
    }
`


// end of file
