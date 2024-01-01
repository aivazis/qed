// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the current selection
export const usePixelPathSelection = (viewport) => {
    // get the active viewport and the current selection
    const { activeViewport, pixelPathSelection } = React.useContext(Context)
    // and return it
    return pixelPathSelection[viewport ?? activeViewport]
}


// end of file
