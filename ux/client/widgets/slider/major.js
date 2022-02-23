// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// local
// hooks
import { useConfig } from "./useConfig"


// render the major tick marks
export const Major = ({ ...rest }) => {

    // get the major tick mark values and the mark generator
    const { major, majorPosition } = useConfig()
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
