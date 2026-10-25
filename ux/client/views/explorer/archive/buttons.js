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


// the cancel button
export const Cancel = styled(EnabledSecondaryButton)``

// the connect button, which says {label}
export const EnabledConnect = ({ connect, label = "connect" }) => {
    // build the handler that registers a new data archive
    const connectArchive = evt => {
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
        onClick: connectArchive,
    }
    // render
    return (
        <EnabledPrimaryButton {...behaviors}>
            {label}
        </EnabledPrimaryButton>
    )
}

// the connect button when disabled
export const DisabledConnect = ({ label = "connect" }) => {
    // render
    return (
        <Button>
            {label}
        </Button>
    )
}


// end of file
