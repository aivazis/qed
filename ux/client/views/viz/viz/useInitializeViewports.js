// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useInitializeViewports = () => {
    // grab the list of {views} and the array of refs from my context
    const { views, viewports, viewportRegistrar } = React.useContext(Context)

    // initialize the array
    viewports.current = new Array(views.length).fill(null)

    // and return them
    return { viewports: viewports.current, viewportRegistrar }
}


// end of file
