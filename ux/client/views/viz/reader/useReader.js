// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the viewport sync registry
export const useReader = () => {
    // grab the reader metadata
    const { reader } = React.useContext(Context)
    // and make it available
    return reader
}


// end of file
