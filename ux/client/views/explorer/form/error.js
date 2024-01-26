// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// render an error message
export const Error = ({ children }) => {
    // render
    return (
        <Box>
            <Mark>!!&nbsp;</Mark>
            <Message>{children}</Message>
        </Box>
    )
}


// the container
const Box = styled.div`
    font-family: inconsolata;
    font-size: large;
    margin: 1rem;
`

const Mark = styled.span`
    color: hsl(0deg, 100%, 50%);
`

// the message
const Message = styled.span`
    color: hsl(0deg, 0%, 40%);
`

// end of file
