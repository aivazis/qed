// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Live as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useLive } from '~/views/viz'
// styles
import styles from './styles'


// opt this viewport into live sync: a client-only preference that pushes its interactions to the
// server on every tick, so peers follow smoothly, instead of once the gesture settles
export const Live = ({ viewport }) => {
    // read this viewport's opt-in and its toggle
    const { enabled, toggle } = useLive(viewport)
    // turn the toggle into an event handler
    const onClick = evt => {
        // keep the click from bubbling up to the bar
        evt.stopPropagation()
        // and from doing anything default
        evt.preventDefault()
        // flip the opt-in
        toggle()
        // all done
        return
    }

    // my event handlers
    const behaviors = {
        // toggle the opt-in on a single click
        onClick,
    }

    // reflect the opt-in in the badge state
    const state = enabled ? "selected" : "enabled"
    // mix my paint
    const paint = styles.live
    // render
    return (
        <Badge size={18} state={state} behaviors={behaviors} style={paint}
            aria-label="toggle live sync" aria-pressed={enabled}
            data-qed-control="viewport" data-qed-action="live" >
            <Shape />
        </Badge >
    )
}


// end of file
