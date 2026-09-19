// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Spinner } from '~/widgets'


// the area
export const Busy = () => {
    // render
    return (
        <Box>
            <Spinner size="150px" />
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


// end of file
