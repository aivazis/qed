// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the {moving} flag
export const useSetMoving = (idx) => {
    // get the flag mutator
    const { setMoving } = React.useContext(Context)

    // make a handler that sets the flag
    const select = () => {
        // set the flag
        setMoving(idx)
    }

    // and return the handler
    return select
}


// end of file
