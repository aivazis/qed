// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'

// local
// hooks
import { useMine } from "./useMine"
import { useNames } from "./useNames"


// draw an axis in the controller native coordinate system
export const Axis = ({ ...rest }) => {
    // get the controller bounding box
    const { mainMine } = useMine()
    // and the names of things
    const { mainCoordinateName, crossCoordinateName } = useNames()

    // orient me
    const axis = {
        [mainCoordinateName]: mainMine,
        [crossCoordinateName]: 0,
    }
    // form my path
    const path = `M 0 0 l ${axis.x} ${axis.y}`

    // render
    return (
        <Path d={path} {...rest} />
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
