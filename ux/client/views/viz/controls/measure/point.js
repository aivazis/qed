// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// a line in the table of the points on the {measure} layer of the active viewport
export const Point = ({ idx, point }) => {
    // make a mark
    return (
        <Box>
            <Index>{idx}:</Index>
            <Icon></Icon>
            <Coordinate>{point[1]}</Coordinate>
            <Coordinate>{point[0]}</Coordinate>
        </Box>
    )
}


// the container
const Box = styled.div`
    font-family: inconsolata;
    font-size: 80%;
    padding: 0.2rem 0.0rem;
`

const Icon = styled.span`
    display: inline-block;
    width: 3.0rem;
    text-align: start;
`

const Index = styled.span`
    display: inline-block;
    width: 2.0rem;
    text-align: end;
`

const Coordinate = styled.span`
    display: inline-block;
    width: 3.75rem;
    text-align: end;
    padding: 0.0rem 0.25rem 0.0rem 0.0rem;
`


// end of file
