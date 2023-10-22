// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useGetActiveView = () => {
    // unpack
    const { views, activeViewport } = React.useContext(Context)
    // grab the view in the active viewport and return it
    return views[activeViewport]
}


// end of file
