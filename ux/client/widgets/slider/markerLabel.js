// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { useConfig } from './useConfig'


// render a single label at the marker position
export const MarkerLabel = ({ value }) => {
    // unpack the geometry
    const { enabled, markers, markerLabelPosition } = useConfig()

    // if the client does not want the value label
    if (!markers) {
        // bail
        return null
    }

    // pick an implementation based on my state
    const Label = enabled ? Enabled : Disabled

    // render
    return (
        <Label {...markerLabelPosition(value)} >
            {value.toFixed(1)}
        </Label>
    )
}


// styling
// the base
const Base = styled.text`
    font-family: inconsolata;
    font-size: 28px;
    text-anchor: middle;
    cursor: default;
`


const Disabled = styled(Base)`
    fill: hsl(0deg, 0%, 20%);
`


const Enabled = styled(Base)`
    fill: hsl(0deg, 0%, 40%);
`


// end of file
