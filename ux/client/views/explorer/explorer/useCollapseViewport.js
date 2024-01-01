// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import {
    Context,
    emptyView,
} from './context'


// build a handler that collapses a given view
export const useCollapseViewport = viewport => {
    // grab the mutators for the set of views and teh active viewport
    const {
        // mutators
        setActiveViewport, setViews,
    } = React.useContext(Context)
    // make a handler that adds a new blank view after a given one
    const collapseViewport = () => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // remove the entry specified by the caller
            clone.splice(viewport, 1)
            // if i'm left with an empty pile
            if (clone.length === 0) {
                // reinitialize
                return [emptyView()]
            }
            // and hand off the new state
            return clone
        })
        // activate the previous view
        setActiveViewport(Math.max(viewport - 1, 0))
        // all done
        return
    }
    // and return it
    return collapseViewport
}


// end of file
