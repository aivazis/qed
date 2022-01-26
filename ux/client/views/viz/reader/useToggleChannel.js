// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the specified {channel} as the selected one
export const useToggleChannel = (value) => {
    // grab the selector mutator
    const { setChannel } = React.useContext(Context)
    // make the toggle
    const toggle = () => {
        // flip the channel selection
        setChannel(old => old === value ? null : value)
        // all done
        return
    }

    // and return it
    return toggle
}


// end of file
