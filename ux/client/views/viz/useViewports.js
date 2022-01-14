// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useViewports = () => {
    // grab the array of refs from my context
    const { viewports } = React.useContext(VizContext)
    // and return its current pile
    return viewports.current
}


// end of file
