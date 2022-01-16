// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// access to the viewport sync registry
export const useSynced = () => {
    // grab the sync table
    const { synced } = React.useContext(VizContext)
    // and return it
    return synced
}


// end of file
