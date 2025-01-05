// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useConfig } from './useConfig'


// render a single label
export const Label = ({ tick, value = null, setValue = null }) => {
    // unpack the geometry
    const { enabled, arrows, labels, labelPosition, tickPrecision } = useConfig()

    // check whether my value is the currently chosen one
    const selected = tick === value
    // if so, and the marker is on the same side of the axis as the labels
    if (selected && arrows === labels) {
        // the marker gets drawn in my place; bail
        return null
    }

    // pick an implementation based on my state
    const Label = enabled ? (selected ? Selected : Enabled) : Disabled

    // set up my behaviors
    const behaviors = {}
    // when have a way to notify the client, am enabled, but not selected
    if (setValue != null && enabled && !selected) {
        // on click, set the value
        behaviors["onClick"] = evt => {
            // suppress the placemat listener
            evt.stopPropagation()
            // set the value
            setValue(tick)
            // all done
            return
        }
    }

    // render
    return (
        <Label {...labelPosition(tick)} {...behaviors} >
            {tick.toFixed(tickPrecision)}
        </Label>
    )
}


// styling
// the base
const Base = styled.text`
    font-family: inconsolata;
    font-size: 32px;
    text-anchor: middle;
    cursor: default;
`


const Disabled = styled(Base)`
    fill: ${props => theme.page.dim};
`


const Enabled = styled(Base)`
    & {
        fill: ${props => theme.page.normal};
        cursor: pointer;
    }

    &:hover {
        fill: ${props => theme.page.highlight};
    }

    &:active {
        fill: ${props => theme.page.highlight};
    }
`


const Selected = styled(Base)`
    fill: ${props => theme.page.highlight};
`


// end of file
