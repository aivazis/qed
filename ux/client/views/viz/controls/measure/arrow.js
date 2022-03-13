// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

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
       fill: hsl(28deg, 90%, 25%);
       stroke: none;
    }

    &:hover {
       fill: hsl(28deg, 90%, 45%);
    }

    &:active {
       fill: hsl(28deg, 90%, 45%);
    }
`

// the arrow
const Shape = styled.path`
    cursor: pointer;
`

// its placemat
const Placemat = styled.path`
    fill: none;
    stroke: hsl(0deg, 0%, 10%);
    stroke-width: 5;
    vector-effect: non-scaling-stroke;
`


// end of file
