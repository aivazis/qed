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
export const useSetBaseZoomLevel = (viewport) => {
    // grab the active viewport and the zoom level table mutator
    const { baseZoom } = React.useContext(Context)
    // get the table
    const table = baseZoom.current
    // update the value for the given {viewport}
    table[viewport] = value
    // all done
    return
}


// end of file
