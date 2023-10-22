// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import {
    Context,
    emptyView,
} from './context'


// build a handler that collapses a given view
export const useCollapseViewport = view => {
    // grab the list of {views} from context
    const {
        // mutators
        setActiveViewport, setViews,
    } = React.useContext(Context)
    // make a handler that adds a new blank view after a given on
    const collapseView = () => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone.splice(view, 1)
            // if i'm left with an empty pile
            if (clone.length === 0) {
                // reinitialize
                return [emptyView()]
            }
            // and hand off the new state
            return clone
        })

        // activate the previous view
        setActiveViewport(Math.max(view - 1, 0))

        // all done
        return
    }
    // and return it
    return collapseView
}


// end of file
