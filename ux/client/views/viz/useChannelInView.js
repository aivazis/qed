// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook to pull the dataset readers out the outlet context
export const useChannelInView = () => {
    // grab the {views} and the index of the {activeView}
    const { activeView, views } = React.useContext(Context)
    // make an accessor
    const getChannelInView = (view = activeView) => ({ ...views[view] })
    // and return it
    return getChannelInView
}


// end of file
