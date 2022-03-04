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
export const usePoints = () => {
    // get the list
    const { points } = React.useContext(Context)
    // and return it
    return points
}


// end of file
