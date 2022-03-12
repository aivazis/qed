// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the current selection
export const useSelection = () => {
    // get the current selection
    const { selection } = React.useContext(Context)
    // and return it
    return selection
}


// end of file
