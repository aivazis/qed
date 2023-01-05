// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// local
// hooks
import { usePixelPath } from '../../../viz/usePixelPath'
// components
import { Profile } from './profile'
import { Point } from './point'
import { Title } from './title'


// a table of the points on the {measure} layer of the active viewport
export const Path = () => {
    // get the set of pixels on the profile path
    const pixelPath = usePixelPath()
    // if the path is empty
    if (pixelPath.length === 0) {
        // bail
        return null
    }

    // otherwise, compute the id of the last point
    const last = pixelPath.length - 1

    // render the points
    return (
        <Box>
            {/* add a title to the table */}
            <Title />
            {/* render the points on the path */}
            {pixelPath.map((point, idx) =>
                <Point key={`p${idx}`} idx={idx} point={point} last={last} />)
            }
            {/* download the profile */}
            <Profile />
        </Box>
    )
}


// the container
const Box = styled.div`
    color: hsl(0deg, 0%, 50%);
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
`


// end of file
