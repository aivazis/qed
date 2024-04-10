// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
    const { reader, sync } = useFragment(syncViewerGetScrollSyncStateFragment, view)
    // unpack the scroll sync status
    const isScrollSynced = sync.scroll

    // get the mutators
    const { toggle: toggleScrollAll } = useSyncToggleAll({
        viewport, reader: reader.name, aspect: "scroll"
    })
    const { toggle: toggleScrollViewport } = useSyncToggleViewport({
        viewport, reader: reader.name, aspect: "scroll"
    })
    // turn the toggle into an event handler
    const toggleViewport = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // flip the state of the scroll sync
        toggleScrollViewport()
        // all done
        return
    }
    // turn the all sync into an event handler
    const toggleAll = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // flip the state of the scroll sync on all viewports
        toggleScrollAll()
        // all done
        return
    }

    // my event handlers
    const behaviors = {
        // toggle the sync state on a single click
        onClick: toggleViewport,
        // toggle all the scroll sync flags on a double click
        onDoubleClick: toggleAll,
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
        reader {
            name
        }
        sync {
            scroll
        }
    }
`


// end of file