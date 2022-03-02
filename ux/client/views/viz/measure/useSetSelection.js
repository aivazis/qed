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
export const useSetSelection = (idx) => {
    // get the selection mutator
    const { setSelection } = React.useContext(Context)

    // make a handler that resets the current selection to the given node
    const select = () => {
        // reset the selection
        setSelection(new Set([idx]))
    }

    // and return the handler
    return select
}


// end of file
