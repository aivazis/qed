// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { usePixelPath } from '../../../../main/usePixelPath'
// components
import { Profile } from './profile'
import { Point } from './point'
import { Title } from './title'


// a table of the points on the {measure} layer of the active viewport
export const Path = () => {
    // get the path profile
    const pixelPath = usePixelPath()
    // and the set of points n the path
    const points = pixelPath.points
    // if the path is empty
    if (points.length === 0) {
        // bail
        return null
    }

    // otherwise, compute the id of the last point
    const last = points.length - 1

    // render the points
    return (
        <Box>
            {/* add a title to the table */}
            <Title />
            {/* render the points on the path */}
            {points.map((point, idx) =>
                <Point key={`p${idx}`} idx={idx} point={point} last={last} />)
            }
            {/* download the profile */}
            <Profile />
        </Box>
    )
}


// the container
const Box = styled.div`
    color: ${() => theme.page.normal};
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
`


// end of file
