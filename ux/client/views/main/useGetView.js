// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook to pull the dataset readers out the outlet context
export const useGetView = viewport => {
    // grab the state of the remote store and te atcive viewport
    const { qed, activeViewport } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // make a copy of the view and return it
    return { ...qed.views[viewport] }
}


// end of file
