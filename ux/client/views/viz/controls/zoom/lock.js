// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

//  display the zoom controller lock
export const Lock = ({ lock, toggle }) => {
    // set up my behaviors
    const behaviors = {
        onClick: toggle,
    }
    // mix my paint
    const Button = lock ? SelectedButton : ActiveButton;
    // and render
    return (
        <Button cx={0} cy={0} r={5} {...behaviors} />
    )
}


// the button
const ActiveButton = styled.circle`
    stroke: ${() => theme.page.normal};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`

const SelectedButton = styled.circle`
    fill: ${() => theme.page.highlight};
`


// end of file
