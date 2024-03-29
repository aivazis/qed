// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { usePixelPath } from '../../../viz/usePixelPath'
import { useSetPixelPath } from '../../../viz/useSetPixelPath'
// components
import { Button } from './button'


// insert a point to the path after the given one
export const Close = () => {
    // get the pixel path of the active viewport
    const pixelPath = usePixelPath()
    // and the path mutator
    const { toggle } = useSetPixelPath()

    // assemble the behaviors
    const behaviors = {
        onClick: toggle,
    }

    // pick the representation based on the current state of the path
    const Toggle = pixelPath.closed ? Closed : Open

    // render
    return (
        <Button behaviors={behaviors}>
            <Toggle cx="500" cy="500" r="450" />
        </Button>
    )
}

const Closed = styled.circle`
    fill: hsl(0deg, 0%, 60%);
`

const Open = styled.circle`
    fill: none;

    stroke: hsl(0deg, 0%, 60%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// end of file
