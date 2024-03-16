// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useConfig } from './useConfig'


// render a single label at the marker position
export const MarkerLabel = ({ value }) => {
    // unpack the geometry
    const { enabled, markers, markerLabelPosition, markerPrecision } = useConfig()

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
            {value.toFixed(markerPrecision)}
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
    fill: ${props => theme.page.dim};
`


const Enabled = styled(Base)`
    fill: ${props => theme.page.normal};
`


// end of file
