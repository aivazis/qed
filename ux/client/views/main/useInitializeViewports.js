// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useInitializeViewports = () => {
    // grab the remote store and the array of refs from my context
    const { qed, viewports, viewportRegistrar } = React.useContext(Context)
    // initialize the array
    viewports.current = new Array(qed.views.length).fill(null)
    // and publish
    return { viewports: viewports.current, viewportRegistrar }
}


// end of file
