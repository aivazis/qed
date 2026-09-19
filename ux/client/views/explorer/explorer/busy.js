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
            <Spinner size="3.0em" />
        </Box>
    )
}

// the box; it centers the spinner by laying it out, since the spinner's transform belongs
// to its animation
const Box = styled.section`
    /* for my container */
    flex: 1 1 auto;
    min-width: 50px;
    /* for my spinner */
    display: flex;
    align-items: center;
    justify-content: center;
`


// end of file
