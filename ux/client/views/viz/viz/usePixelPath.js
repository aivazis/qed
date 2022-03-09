// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the list of points in the profile
export const usePixelPath = (viewport = null) => {
    // get the list and the active viewport
    const { activeViewport, pixelPath } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // and return it
    return pixelPath[viewport]
}


// end of file
