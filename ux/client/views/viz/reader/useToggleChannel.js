// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useVisualize } from '../viz/useVisualize'
// context
import { Context } from './context'
import { useReader } from './useReader'
import { useDataset } from './useDataset'


// toggle the {coordinate} as the value for {axis}
export const useToggleChannel = (value) => {
    // grab the selector mutator
    const { setChannel } = React.useContext(Context)
    // the current reader
    const reader = useReader()
    // the current dataset
    const dataset = useDataset()
    // and the mutator of the current view
    const visualize = useVisualize()

    // make the toggle
    const toggle = () => {
        // make room
        let channel = null
        // adjust the selector
        setChannel(old => {
            // flip the state
            channel = old === value ? null : value
            // and return it
            return channel
        })
        // update the active view
        visualize({ reader, dataset, channel })
        // all done
        return
    }

    // and return it
    return toggle
}


// end of file
