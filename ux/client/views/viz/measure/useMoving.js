// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the moving indicator
export const useMoving = () => {
    // get the flag
    const { moving } = React.useContext(Context)
    // and return it
    return moving
}


// end of file
