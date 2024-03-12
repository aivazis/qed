// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook that adjusts the contents of a given viewport
// currently, only called by {reader} instances when selected/updated
export const useVisualize = () => {
    // grab the active viewport index and the {views} mutator
    const { activeViewport, setViews, synced } = React.useContext(Context)

    // make the handler
    const visualize = (view, viewport = activeViewport) => {
        // unpack the view
        const { channel } = view
        // adjust the view
        setViews(old => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry specified by the caller
            clone[viewport] = { ...old[viewport], ...view }
            // if i'm channel synced
            if (synced[viewport].channel) {
                // go through the sync table
                synced.forEach((sync, port) => {
                    // if this port is channel synced and it understands this channel
                    if (sync.channel && clone[port].dataset.channels.includes(channel)) {
                        // adjust the channel
                        clone[port].channel = channel
                    }
                    // all done
                    return
                })
            }
            // and hand off the new state
            return clone
        })
        // all done
        return
    }

    // and return it
    return visualize
}


// end of file
