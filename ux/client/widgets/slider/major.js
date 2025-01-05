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


// render the major tick marks
export const Major = ({ setValue = null, ...rest }) => {
    // get the major tick mark values and the mark generator
    const { enabled, major, majorPosition } = useConfig()
    // build a handler factory that uses my exact value
    const pick = value => {
        // make a handler
        return evt => {
            // suppress the placemat listener
            evt.stopPropagation()
            // quash any side effects
            evt.preventDefault()
            // set the value
            setValue(value)
            // all done
            return
        }
    }
    // render
    return (
        <g>
            {major.map(tick => {
                // pick an implementation based on my state
                const Path = enabled ? Enabled : Disabled
                // build my behaviors
                const behaviors = setValue ? { onClick: pick(tick) } : {}
                // render
                return (
                    <Path key={tick} d={majorPosition(tick)} {...behaviors} {...rest} />
                )
            })}
        </g>
    )
}


// styling
const Base = styled.path`
    fill: none;
    stroke-width: 1;
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
        stroke: ${props => theme.page.highlight};
    }

    &:active {
        stroke: ${props => theme.page.highlight};
    }
`


// end of file
