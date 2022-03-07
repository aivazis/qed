// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// local
// components
import { Point } from './point'
import { Title } from './title'


// a table of the points on the {measure} layer of the active viewport
export const Path = ({ path }) => {
    // if the path is empty
    if (path.length === 0) {
        // bail
        return null
    }

    // otherwise, render the points
    return (
        <Box>
            {/* add a title to the table */}
            <Title />
            {/* render the points on the path */}
            {path.map((point, idx) => <Point key={`p${idx}`} idx={idx} point={point} />)}
        </Box>

    )
}


// the container
const Box = styled.div`
    padding: 1.0rem;
`


// end of file
