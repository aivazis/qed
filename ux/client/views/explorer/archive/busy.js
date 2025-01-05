// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// the area
export const Busy = () => {
    // render
    return (
        <Box>
            <Indicator />
        </Box>
    )
}

// the box
const Box = styled.section`
    display: flex;
    margin: 5.0rem 0.0em auto 0.0em;
    justify-content: center;
    align-items: center;
`

// the busy indicator
const Indicator = styled.div`
    width: 150px;
    height: 150px;
    border: 3px solid hsl(28deg, 90%, 55%);
    border-radius: 50%;
    border-top: 3px solid hsl(28deg, 90%, 55%, 0.5);
    animation: busy 1s linear infinite;
`


// end of file
