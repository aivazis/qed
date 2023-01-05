// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// viewport registration
export const useGetViewportSync = (viewport) => {
    // grab the sync table
    const { synced } = React.useContext(Context)
    // and return the state of the {viewport}
    return synced[viewport]
}


// end of file
