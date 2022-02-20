// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'


// draw an axis in the controller native coordinate system
export const Axis = ({ geometry, ...rest }) => {
    // unpack
    const { axis } = geometry
    // render
    return (
        <Path d={axis} {...rest} />
    )
}


// styling
const Path = styled.path`
    fill: none;
    stroke: hsl(0deg, 0%, 60%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// end of file
