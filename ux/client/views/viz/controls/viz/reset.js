// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Refresh as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// styles
import styles from './styles'


// reset the state of a controller
export const Reset = ({ reset, enabled }) => {

    // build the handler
    const click = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // reset the state
        reset()
        // all done
        return
    }
    // assemble the controllers to hand my {badge}
    const behaviors = {
        onClick: click,
    }

    // deduce my state
    const state = enabled ? "enabled" : "disabled"

    // mix my paint
    const paint = styles.reset
    // and render
    return (
        <Badge size={24} state={state} behaviors={behaviors} style={paint} >
            <Icon />
        </Badge>
    )
}


// end of file