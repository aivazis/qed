// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the viewport sync registry
export const useSynced = () => {
    // grab the sync table
    const { synced } = React.useContext(Context)
    // and return it
    return synced
}


// end of file
