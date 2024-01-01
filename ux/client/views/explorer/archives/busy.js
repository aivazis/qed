// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
    flex: 1 1 auto;
    height: 4.0rem;
    min-width: 4.0rem;
`

// the busy indicator
const Indicator = styled.div`
    display: block;
    position: relative;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 3.0em;
    height: 3.0em;
    border: 3px solid hsl(28deg, 90%, 55%);
    border-radius: 50%;
    border-top: 3px solid hsl(28deg, 90%, 55%, 0.5);
    animation: busy 1s linear infinite;
`


// end of file
