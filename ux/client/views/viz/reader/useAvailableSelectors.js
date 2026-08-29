// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the set of selection candidates
export const useAvailableSelectors = (axis) => {
    // grab the table of candidates
    const { available } = React.useContext(Context)
    // and return the set of possible values for {axis}; an axis with no known values,
    // e.g. on a reader that has not yet completed first contact, gets the empty set, so
    // its coordinates render as unavailable until the discovered catalog arrives
    return available.get(axis) ?? empty
}

// the shared empty set, so passive renders get a referentially stable value
const empty = new Set()


// end of file
