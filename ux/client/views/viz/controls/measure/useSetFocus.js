// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the focus to a single node
export const useSetFocus = (idx) => {
    // get the focus mutator
    const { setFocus } = React.useContext(Context)

    // make a handler that toggles the focus
    const focus = () => {
        // toggle the focus
        setFocus(old => old === idx ? null : idx)
        // all done
        return
    }

    // make a handler that clears the focus iff the current node is focused
    const clear = () => {
        // if {idx} is the focus, clear it; otherwise, leave it alone
        setFocus(old => old === idx ? null : old)
        // all done
        return
    }


    // and return the handlers
    return { clear, focus }
}


// end of file
