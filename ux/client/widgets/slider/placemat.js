// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'


// a workaround for capturing events in the controller client area
// needed only because {pointer-events: bounding-box} doesn't work yet
export const Placemat = ({ geometry, ...rest }) => {
    // unpack the geometry to get the bounding box
    const { boundingBox } = geometry

    // render
    return (
        <Rect {...boundingBox} {...rest} />
    )
}


// styling
const Rect = styled.rect`
    fill: hsl(0deg, 0%, 7%);
    stroke: none;
`

// end of file
