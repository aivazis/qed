// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook to pull the dataset readers out the outlet context
export const useGetView = () => {
    // grab the {views} and the index of the {activeViewport}
    const { activeViewport, views } = React.useContext(Context)
    // make a copy of the active view and return it
    return { ...views[activeViewport] }
}


// end of file
