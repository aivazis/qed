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
    const { setViews, setSynced, setActiveView } = React.useContext(VizContext)
    // make a handler that adds a new blank view after a given on
    const collapseView = () => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone.splice(view, 1)
            // and hand off the new state
            return clone
        })
        // remove its flag from the sync table
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // remove the status of the current view
            table.splice(view, 1)
            // return the new table
            return table
        })
        // activate the previous view
        setActiveView(Math.max(view - 1, 0))
        // all done
        return
    }
    // and return it
    return collapseView
}


// end of file
