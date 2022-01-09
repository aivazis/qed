// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './context'


// hook to pull the dataset readers out the outlet context
export const useVisualizeChannel = () => {
    // grab the readers
    const { activeView, setViews } = React.useContext(VizContext)

    // make the handler
    const visualizeChannel = (channel, view = activeView) => {
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone[view] = channel
            // and hand off the new state
            return clone
        })
        // all done
        return
    }

    // and return it
    return visualizeChannel
}


// end of file
