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
                cursor
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
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
`


// end of file
