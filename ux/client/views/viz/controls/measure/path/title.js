// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// a table of the points on the {measure} layer of the active viewport
export const Title = () => {
    // make a mark
    return (
        <Box>
            <Name>path</Name>
            <Header>line</Header>
            <Header>sample</Header>
        </Box>

    )
}


// the container
const Box = styled.div`
    font-family: rubik-light;
    font-size: 65%;
`

const Name = styled.span`
    display: inline-block;
    width: 1.5rem;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
    color: hsl(0deg, 0%, 75%);
    cursor: default;
`

const Header = styled.span`
    display: inline-block;
    width: 3.0rem;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.25rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
    cursor: default;
`


// end of file
