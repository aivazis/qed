// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'


// render a single label
export const Label = ({ tick, value, setValue, geometry, enabled }) => {
    // unpack the geometry
    const { arrow, labels, labelPosition } = geometry

    // check whether my value is the currently chosen one
    const selected = tick == value
    // if so, and the marker is on the same side of the axis as the labels
    if (selected && arrow === labels) {
        // the marker gets drawn in my place; bail
        return null
    }

    // pick an implementation based on my state
    const Tick = enabled ? (selected ? Selected : Enabled) : Disabled

    // set up my behaviors
    const behaviors = {}
    // when i'm enabled but not selected
    if (enabled && !selected) {
        // on click, set the value
        behaviors["onClick"] = () => setValue(tick)
    }

    // render
    return (
        <Tick {...labelPosition(tick)} {...behaviors} >
            {tick}
        </Tick>
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
    fill: hsl(0deg, 0%, 20%);
`


const Enabled = styled(Base)`
    & {
        fill: hsl(0deg, 0%, 40%);
        cursor: pointer;
    }

    &:hover {
        fill: hsl(0deg, 0%, 75%);
    }

    &:active {
        fill: hsl(28deg, 90%, 55%);
    }
`


const Selected = styled(Base)`
    fill: hsl(28deg, 90%, 55%);
`


// end of file
