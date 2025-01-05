// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// render an error message
export const Error = ({ errors }) => {
    // normalize the errors into an array of strings
    const msgs = (Array.isArray(errors) ? errors : [errors]).map(error => error?.toString())
    // render
    return (
        <Box>
            {msgs.map((msg, idx) => {
                return (
                    <Entry key={idx}>
                        <Mark>!!</Mark>
                        &nbsp;
                        <Message>{msg}</Message>
                    </Entry>
                )
            })}
        </Box>
    )
}


// the container
const Box = styled.div`
    font-family: inconsolata;
    font-size: medium;
    margin: 1rem;
`

const Entry = styled.div`
    display: flex;
    flex-direction: row;
    white-space: nowrap;
    text-overflow: ellipsis;
    line-height: 150%;
`

const Mark = styled.span`
    color: hsl(0deg, 100%, 50%);
`

// the message
const Message = styled.span`
    color: hsl(0deg, 0%, 40%);
`

// end of file
