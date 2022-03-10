// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// local
// hooks
import { useFocus } from './useFocus'


// a table of the points on the {measure} layer of the active viewport
export const Minimap = ({ path }) => {
    // get the node in focus
    const focus = useFocus()

    // if it's still uninitialized
    if (focus === null) {
        // bail
        return null
    }

    // render
    return (
        <Box>
        </Box>
    )
}


// the container
const Box = styled.div`
    width: 256px;
    height: 256px;
    background-color: hsl(0deg, 0%, 10%);
    margin: 0.0rem 1.0rem 1.0rem 1.0rem;
`


// end of file
