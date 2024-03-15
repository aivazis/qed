// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Download as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// styles
import styles from './styles'


// save the state of a controller
export const Save = ({ save, enabled }) => {

    // build the handler
    const click = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // save the state
        save()
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
    const paint = styles.save
    // and render
    return (
        <Badge size={16} state={state} behaviors={behaviors} style={paint}
            title="save the current values as the default"
        >
            <Icon />
        </Badge>
    )
}


// end of file