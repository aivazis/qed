// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


//  a toggle
export const Toggle = ({ state, toggle, force }) => {
    // build the event handler for flipping my state
    const flip = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // check the status of the <Alt> key
        const { altKey } = evt
        // flip the state
        altKey ? force() : toggle()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        // on click, toggle my state
        onClick: flip,
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
    & {
        border-color: hsl(0deg, 0%, 40%);
    }

    &:hover {
        border-color: hsl(28deg, 90%, 45%);
    }
`

const SelectedButton = styled(Button)`
    background-color: hsl(28deg, 90%, 45%);
    border-color: hsl(28deg, 90%, 45%);
`


// end of file
