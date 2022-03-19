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
export const useGetView = viewport => {
    // grab the {views} and the index of the {activeViewport}
    const { activeViewport, views } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // make a copy of the view and return it
    return { ...views[viewport] }
}


// end of file
