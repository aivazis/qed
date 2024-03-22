// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the specified {client} channel as the selected one
export const useToggleChannel = client => {
    // grab the channel ref
    const { channel } = React.useContext(Context)

    // make the toggle
    const toggle = () => {
        // flip the channel selection
        channel.current = channel.current?.tag === client.tag ? null : client
        // all done
        return
    }

    // and return it
    return toggle
}


// end of file
