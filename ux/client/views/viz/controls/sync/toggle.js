// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


//  a toggle
export const Toggle = ({ state, toggle }) => {
    // set up my behaviors
    const behaviors = {
        // on click, toggle my state
        onClick: toggle,
    }
    // mix my paint
    const Control = state ? SelectedButton : ActiveButton;
    // and render
    return (
        <Control {...behaviors} />
    )
}


// the housing
const Button = styled.div`
    margin: 0.0 auto;
    width: 0.75em;
    height: 0.75em;
    background-color: none;
    border-width: 1px;
    border-style: solid;
    border-radius: 50%;
    cursor: pointer;
`

// the  button
const ActiveButton = styled(Button)`
    border-color: (0deg, 0%, 40%);
`

const SelectedButton = styled(Button)`
    background-color: hsl(28deg, 90%, 45%);
    border-color: hsl(28deg, 90%, 45%);
`


// end of file
