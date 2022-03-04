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
export const useStartMoving = (idx) => {
    // get the mutator of the movement indicator
    const { setMoving } = React.useContext(Context)

    // make a handler that marks my node as the movement initiator
    const select = () => {
        // mark
        setMoving(idx)
        // all done
        return
    }

    // and return the handler
    return select
}


// end of file
