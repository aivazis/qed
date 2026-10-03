// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'


// local
// components
import { Button, EnabledPrimaryButton, EnabledSecondaryButton } from '../form'


// the cancel button, marked as a button so drivers can find it
export const Cancel = styled(EnabledSecondaryButton).attrs({ role: "button" })``

// the connect button
export const EnabledConnect = ({ connect }) => {
    // build the handler that registers a new reader
    const connectReader = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // connect the dataset to its reader
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
        <EnabledPrimaryButton
            role="button" aria-label="connect this dataset" aria-disabled={false} {...behaviors}>
            connect
        </EnabledPrimaryButton>
    )
}

// the connect button when disabled
export const DisabledConnect = ({ children }) => {
    // render
    return (
        <Button role="button" aria-label="connect this dataset" aria-disabled={true}>
            connect
        </Button>
    )
}


// end of file
