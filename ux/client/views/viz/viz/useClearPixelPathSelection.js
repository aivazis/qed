// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// clear the current selection
export const useClearSelection = (idx) => {
    // get the selection mutator
    const { setSelection } = React.useContext(Context)

    // make a handler that clears the current selection
    const clear = () => {
        // reset the selection to an empty set
        setSelection(new Set())
    }

    // and return the handler
    return clear
}


// end of file
