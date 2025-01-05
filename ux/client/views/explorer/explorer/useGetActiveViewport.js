// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// get the index of the active viewport
export const useGetActiveViewport = () => {
    // grab the active viewport index from context
    const { activeViewport } = React.useContext(Context)
    // and return it
    return activeViewport
}


// end of file
