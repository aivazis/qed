// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'


// render the major tick marks
export const Major = ({ geometry, ...rest }) => {

    // get the major tickmark values and the mark generator
    const { major, majorPosition } = geometry
    // generate them
    const ticks = major.map(value => majorPosition(value)).join(" ")

    // render
    return (
        <Path d={ticks} {...rest} />
    )
}


// styling
const Path = styled.path`
    fill: none;
    stroke: hsl(0deg, 0%, 40%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// end of file
