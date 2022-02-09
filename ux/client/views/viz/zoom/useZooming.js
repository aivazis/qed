// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the zoom level of the active viewport
export const useZooming = () => {
    // grab the zooming indicator
    const { zooming } = React.useContext(Context)
    // and return it
    return zooming
}


// end of file
