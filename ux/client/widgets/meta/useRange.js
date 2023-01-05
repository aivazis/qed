// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the detail range
export const useRange = () => {
    // grab the detail range
    const { range } = React.useContext(Context)
    // unpack
    const [min, max] = range
    // and return it
    return { min, max }
}


// end of file
