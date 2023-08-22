// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the set of selection candidates
export const useCandidates = (axis) => {
    // grab the table of candidates
    const { candidates } = React.useContext(Context)
    // and return the set of possible values for {axis}
    return candidates.get(axis)
}


// end of file
