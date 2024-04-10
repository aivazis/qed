// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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

// the scroll sync control
export const Scroll = ({ viewport, view, mark }) => {
    // unpack the view
    const { sync } = useFragment(scrollSyncTableFragment, view)
    // build the handler that toggles all viewports
    const { toggle: toggleAll } = useSyncToggleAll()
    // and the single viewport toggle
    const { toggle: toggleViewport } = useSyncToggleViewport()

    // specialize them
    const toggleScroll = () => {
        // toggle the scroll entry of the sync table for this viewport
        toggleViewport({ viewport, aspect: "scroll" })
        // all done
        return
    }
    const toggleAllScroll = () => {
        // toggle the scroll entry of the sync table for this viewport
        toggleAll({ viewport, aspect: "scroll" })
        // all done
        return
    }

    // render
    return (
        <Control>
            <Toggle
                state={sync.scroll} mark={mark}
                toggle={toggleScroll} force={toggleAllScroll}
            />
        </Control>
    )
}


const scrollSyncTableFragment = graphql`
    fragment scrollSyncTableFragment on View {
        sync {
            scroll
        }
    }
`


// end of file
