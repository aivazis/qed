// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the viewport sync registry
export const useChannel = () => {
    // grab the channel ref
    const { channel } = React.useContext(Context)
    // and return its current value
    return channel.current
}


// end of file
