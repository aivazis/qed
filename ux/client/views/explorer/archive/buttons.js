// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


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
    // build the handler that creates a new record
    const createRecord = evt => {
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
        onClick: createRecord,
    }
    // render
    return (
        <EnabledPrimaryButton {...behaviors}>
            connect
        </EnabledPrimaryButton>
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