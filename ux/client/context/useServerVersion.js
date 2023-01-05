// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the viewport sync registry
export const useServerVersion = () => {
    // grab the reader metadata
    const { serverVersion } = React.useContext(Context)
    // and return it
    return serverVersion
}


// end of file
