// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// hooks
import { useSyncToggleAll } from './useSyncToggleAll'
import { useSyncToggleViewport } from './useSyncToggleViewport'
// components
import { Control } from './control'
import { Toggle } from './toggle'

// the channel sync control
export const Channel = ({ viewport, view, mark }) => {
    // unpack the view
    const { sync } = useFragment(channelSyncTableFragment, view)
    // build the handler that toggles all viewports
    const { toggle: toggleAll } = useSyncToggleAll()
    // and the single viewport toggle
    const { toggle: toggleViewport } = useSyncToggleViewport()

    // specialize them
    const toggleChannel = () => {
        // toggle the channel entry of the sync table for this viewport
        toggleViewport({ viewport, aspect: "channel" })
        // all done
        return
    }
    const toggleAllChannels = () => {
        // toggle the channel entry of the sync table for this viewport
        toggleAll({ viewport, aspect: "channel" })
        // all done
        return
    }

    // render
    return (
        <Control>
            <Toggle state={sync.channel} mark={mark}
                toggle={toggleChannel} force={toggleAllChannels}
            />
        </Control>
    )
}


const channelSyncTableFragment = graphql`
    fragment channelSyncTableFragment on View {
        sync {
            channel
        }
    }
`


// end of file
