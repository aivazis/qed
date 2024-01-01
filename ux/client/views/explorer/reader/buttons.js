// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'


// local
// components
import { Button, EnabledPrimaryButton, EnabledSecondaryButton } from '../form'


// the cancel button
export const Cancel = styled(EnabledSecondaryButton)``

// the connect button
export const EnabledConnect = ({ connect }) => {
    // build the handler that registers a new reader
    const connectReader = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // add the data archive to the pile
        connect()
        // all done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: connectReader,
    }
    // render
    return (
        <EnabledPrimaryButton {...behaviors}>
            connect
        </EnabledPrimaryButton>
    )
    // otherwise, resolve the connector
    // and render it
    return (
        null
    )
}

// the connect button when disabled
export const DisabledConnect = ({ children }) => {
    // render
    return (
        <Button>
            connect
        </Button>
    )
}

// end of file