// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { ViewportContext } from './viewportContext'


// get the viewport position
export const useGetViewportCameraZoom = () => {
    // grab the value
    const { zoom } = React.useContext(ViewportContext)
    // and return it
    return zoom
}


// end of file
