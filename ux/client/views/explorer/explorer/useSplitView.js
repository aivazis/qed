// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// build a handler that splits a view
export const useSplitView = view => {
    // grab what i need from the context
    const {
        // mutators
        setActiveViewport, setViews,
    } = React.useContext(Context)

    // make a handler that adds a new blank view after a given on
    const splitView = () => {

        // add a new view to the pile
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // the new view is a copy of the view being split
            clone.splice(view + 1, 0, old[view])
            // all done
            return clone
        })

        // activate the new view
        setActiveViewport(view + 1)

        // all done
        return
    }

    // and return it
    return splitView
}


// end of file
