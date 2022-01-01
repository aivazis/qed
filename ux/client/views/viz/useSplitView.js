// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useSplitView = view => {
    // grab the list of {views} from context
    const { setViews, setActiveView } = React.useContext(Context)
    // make a handler that adds a new blank view after a given on
    const splitView = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // make a copy of the current view
            clone.splice(view + 1, 0, old[view])
            // and make it the active one
            setActiveView(view + 1)
            // and hand off the new state
            return clone
        })
        // all done
        return
    }
    // and return it
    return splitView
}


// end of file
