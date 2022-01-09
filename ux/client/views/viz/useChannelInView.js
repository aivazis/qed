// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './context'


// hook to pull the dataset readers out the outlet context
export const useChannelInView = () => {
    // grab the {views} and the index of the {activeView}
    const { activeView, views } = React.useContext(VizContext)
    // make an accessor
    const getChannelInView = (view = activeView) => ({ ...views[view] })
    // and return it
    return getChannelInView
}


// end of file
