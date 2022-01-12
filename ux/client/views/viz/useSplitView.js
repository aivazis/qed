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
export const useSplitView = view => {
    // grab the list of {views} from context
    const { setViews, setSynced, setActiveView } = React.useContext(VizContext)
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
        // initialize its sync status
        setSynced(old => {
            // make a copy of the old table
            const table = [...old]
            // add the new viewport at {idx} with a default state
            table.splice(view + 1, 0, false)
            // return the new table
            return table
        })
        // activate the new view
        setActiveView(view + 1)

        // all done
        return
    }
    // and return it
    return splitView
}


// end of file
