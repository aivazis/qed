// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// clear the {moving} flag
export const useStopMoving = () => {
    // get the flag mutator
    const { setMoving } = React.useContext(Context)

    // make a handler that clears the movement indicator
    const clear = () => {
        // clear the flag
        setMoving(null)
        // all done
        return
    }

    // and return the handler
    return clear
}


// end of file
