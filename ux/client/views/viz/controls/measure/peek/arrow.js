// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// an arrow
export const Arrow = ({ placement, path, behaviors }) => {
    // render
    return (
        <Container transform={placement}>
            <Placemat d={path} />
            <Shape d={path} {...behaviors} />
        </Container>
    )
}


// the container
const Container = styled.g`
    & {
       fill: ${() => theme.page.highlight};
       stroke: none;
    }

    &:hover {
       fill: ${() => theme.page.highlight};
    }

    &:active {
       fill: ${() => theme.page.highlight};
    }
`

// the arrow
const Shape = styled.path`
    cursor: pointer;
`

// its placemat
const Placemat = styled.path`
    fill: none;
    stroke: ${() => theme.page.relief};
    stroke-width: 5;
    vector-effect: non-scaling-stroke;
`


// end of file
