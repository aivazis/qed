// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useInitializeViewports = views => {
    // grab the remote store and the array of refs from my context
    const { viewports, viewportRegistrar } = React.useContext(Context)
    // initialize the array
    viewports.current = new Array(views.length).fill(null)
    // and publish
    return { viewports: viewports.current, viewportRegistrar }
}


// end of file
