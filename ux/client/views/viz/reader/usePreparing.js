// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
import { Context } from './context'


// access to whether the dataset of the active view is still being prepared
export const usePreparing = () => {
    // grab the flag
    const { preparing } = React.useContext(Context)
    // and return it
    return preparing
}


// end of file
