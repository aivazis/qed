// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// clear the current selection
export const useClearPixelPath = viewport => {
    // get the selection mutator
    const { activeViewport, setPixelPath } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport

    // make a handler that clears the current selection
    const clear = () => {
        // reset the selection to an empty set
        setPixelPath(old => {
            // make a copy
            const paths = [...old]
            // clear out the one that corresponds to {viewport}
            paths[viewport] = []
            // and return the new pile
            return paths
        })
        // all done
        return
    }

    // and return the handler
    return clear
}


// end of file
