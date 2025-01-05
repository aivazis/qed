// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from "react"
import styled from 'styled-components'
import { useConfig } from "./useConfig"

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useMine } from "./useMine"
import { useNames } from "./useNames"


// draw an axis in the controller native coordinate system
export const Axis = ({ ...rest }) => {
    // get my state
    const { enabled } = useConfig()
    // get the controller bounding box
    const { mainMine } = useMine()
    // and the names of things
    const { mainCoordinateName, crossCoordinateName } = useNames()

    // orient me
    const axis = {
        [mainCoordinateName]: mainMine,
        [crossCoordinateName]: 0,
    }
    // pick an implementation based on my state
    const Path = enabled ? Enabled : Disabled
    // form my path
    const path = `M 0 0 l ${axis.x} ${axis.y}`

    // render
    return (
        <Path d={path} {...rest} />
    )
}


// styling
const Base = styled.path`
    fill: none;
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


const Disabled = styled(Base)`
    stroke: ${theme.page.dim};
`


const Enabled = styled(Base)`
    stroke: ${theme.page.normal};
`


// end of file
