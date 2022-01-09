// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// access to the registered views
export const useCollapseView = view => {
    // grab the list of {views} from context
    const { setViews, setActiveView } = React.useContext(VizContext)
    // make a handler that adds a new blank view after a given on
    const collapseView = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone.splice(view, 1)
            // and make it the active one
            setActiveView(Math.max(view - 1, 0))
            // and hand off the new state
            return clone
        })
        // all done
        return
    }
    // and return it
    return collapseView
}


// end of file
