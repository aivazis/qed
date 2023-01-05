// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the sync status of this viewport
export const useGetZoomLevel = (viewport) => {
    // grab the active viewport and the zoom table
    const { activeViewport, zoom } = React.useContext(Context)

    // return the zoom level of the active viewport
    return zoom[viewport ?? activeViewport]
}


// end of file
