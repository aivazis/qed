// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shapes
import { Eye as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useSyncToggleAll, useSyncToggleViewport } from '~/views/viz/controls'
// styles
import styles from './styles'


// control viewport synchronization with a shared camera
export const Sync = ({ viewport, view }) => {
    // get the reader and sync status for this viewport
    const { sync } = useFragment(syncViewerGetScrollSyncStateFragment, view)
    // unpack the scroll sync status
    const isScrollSynced = sync.scroll

    // get the mutators
    const { toggle: toggleAll } = useSyncToggleAll()
    const { toggle: toggleViewport } = useSyncToggleViewport()
    // turn the toggle into an event handler
    const toggleScroll = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // get the state of the <alt> key
        const { altKey } = evt
        // set up the handler arguments
        const argv = { viewport, aspect: "scroll" }
        // pick a behavior
        const toggle = altKey ? toggleAll : toggleViewport
        // and invoke it
        toggle(argv)
        // all done
        return
    }

    // my event handlers
    const behaviors = {
        // toggle the sync state on a single click
        onClick: toggleScroll,
    }

    // set my state
    const state = isScrollSynced ? "selected" : "enabled"
    // mix my paint
    const paint = styles.sync
    // render
    return (
        <Badge size={18} state={state} behaviors={behaviors} style={paint} >
            <Shape />
        </Badge >
    )
}

// my fragment
const syncViewerGetScrollSyncStateFragment = graphql`
    fragment syncViewerGetScrollSyncStateFragment on View {
        sync {
            scroll
        }
    }
`


// end of file