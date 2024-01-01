// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// clear the current selection
export const useClearPixelPathSelection = (viewport) => {
    // get the selection mutator
    const { activeViewport, setPixelPathSelection } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport

    // make a handler that clears the current selection
    const clear = () => {
        // reset the selection to an empty set
        setPixelPathSelection(old => {
            // make a copy
            const table = [...old]
            // replace the entry for {viewport} with an empty set
            table[viewport] = new Set()
            // and return the new pile
            return table
        })
        // all done
        return
    }

    // and return the handler
    return clear
}


// end of file
