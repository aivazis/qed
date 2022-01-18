// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Eye as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useGetViewportSync } from '../viz/useGetViewportSync'
import { useToggleViewportSync } from '../viz/useToggleViewportSync'
import { useSyncAllViewports } from '../viz/useSyncAllViewports'
// styles
import styles from './styles'


// control viewport synchronization with a shared camera
export const Sync = ({ viewport }) => {
    // look up the current sync state of the {viewport}
    const isSynced = useGetViewportSync(viewport)
    // build the sync toggle
    const toggle = useToggleViewportSync(viewport)
    // and the one that syncs all them
    const syncAll = useSyncAllViewports(viewport)

    // my event handlers
    const behaviors = {
        // make a handler one that toggles the sync state
        onClick: (evt) => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // quash the default behavior
            evt.preventDefault()
            // flip the state
            toggle()
            // all done
            return
        },
        // and another one that toggles all them to be like me
        onDoubleClick: (evt) => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // quash the default behavior
            evt.preventDefault()
            // flip the state
            syncAll()
            // all done
            return
        },
    }

    // set my state
    const state = isSynced ? "engaged" : "available"
    // grab my style
    const paint = styles.sync
    // mix the shape paint
    const shapePaint = {
        // for the icon
        icon: {
            // the base style
            ...paint.icon,
            // and the state dependent enhancements
            ...paint[state]?.icon,
        },
        // and its details
        decoration: {
            // the base style
            ...paint.decoration,
            // and the state dependent enhancements
            ...paint[state]?.decoration,
        },
    }

    // render
    return (
        <Badge size={16} state={state} behaviors={behaviors} style={paint} >
            <Shape style={shapePaint} />
        </Badge >
    )
}


// end of file