// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the base zoom level table
export const useBaseZoom = () => {
    // grab the base zoom level
    const { baseZoom } = React.useContext(Context)
    // and return it
    return { baseZoom }
}


// end of file
