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


// render the minor tick marks
export const Minor = ({ setValue = null, ...rest }) => {

    // get the minor tick mark values and the mark generator
    const { enabled, minor, minorPosition } = useConfig()
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
            {minor.map(tick => {
                // pick an implementation based on my state
                const Path = enabled ? Enabled : Disabled
                // build my behaviors
                const behaviors = setValue ? { onClick: pick(tick) } : {}
                // render
                return (
                    <Path key={tick} d={minorPosition(tick)} {...behaviors} {...rest} />
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
