// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// local
// components
import { Track } from './track'


// a table with the cursor location and the pixel value
export const Cursor = () => {
    // render the points
    return (
        <Box>
            {/* add a title to the table */}
            <Title>
                <Name>cursor</Name>
                <Header>line</Header>
                <Header>sample</Header>
            </Title>
            {/* place the cursor position and the pixel value */}
            <Track />
        </Box>
    )
}


// the container
const Box = styled.div`
    color: hsl(0deg, 0%, 50%);
    margin: 1.0rem;
`

const Title = styled.div`
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
    /* border-bottom: 1px solid hsl(0deg, 0%, 30%); */
`

const Header = styled.span`
    display: inline-block;
    width: 3.0rem;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.25rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
    /* border-bottom: 1px solid hsl(0deg, 0%, 30%); */
`





// end of file
