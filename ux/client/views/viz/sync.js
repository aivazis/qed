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
import { useGetViewportSync } from './useGetViewportSync'
import { useToggleViewportSync } from './useToggleViewportSync'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Sync = ({ idx }) => {
    // look up the current sync state of the {viewport}
    const isSynced = useGetViewportSync(idx)
    // build the sync toggle
    const toggle = useToggleViewportSync(idx)

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
    }

    // set my state
    const state = isSynced ? "engaged" : "available"
    // grab my style
    const syncStyle = styles.sync
    // mix the shape paint
    const shapeStyle = {
        // for the icon
        icon: {
            // the base style
            ...syncStyle.icon,
            // and the state dependent enhancements
            ...syncStyle[state]?.icon,
        },
        // and its details
        decoration: {
            // the base style
            ...syncStyle.decoration,
            // and the state dependent enhancements
            ...syncStyle[state]?.decoration,
        },
    }

    // render
    return (
        <Badge size={16} state={state} behaviors={behaviors} style={syncStyle} >
            <Shape style={shapeStyle} />
        </Badge >
    )
}


// end of file