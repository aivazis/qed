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
export const useViewports = () => {
    // grab the array of refs from my context
    const { activeViewport, setActiveViewport, viewports } = React.useContext(Context)
    // and return its current pile
    return { activeViewport, setActiveViewport, viewports: viewports.current }
}


// end of file
