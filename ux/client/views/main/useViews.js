// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useViews = () => {
    // grab the store and the active viewport from context
    const { qed, activeViewport } = React.useContext(Context)
    // extract the active views and return them along with the active viewport
    return { views: qed.views, activeViewport }
}


// end of file
