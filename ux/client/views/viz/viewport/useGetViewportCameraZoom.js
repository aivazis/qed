// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// get the viewport position
export const useGetViewportCameraZoom = () => {
    // grab the value
    const { zoom } = React.useContext(Context)
    // and return it
    return zoom
}


// end of file
