// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the set of selection candidates
export const useAvailableSelectors = (axis) => {
    // grab the table of candidates
    const { available } = React.useContext(Context)
    // and return the set of possible values for {axis}
    return available.get(axis)
}


// end of file
