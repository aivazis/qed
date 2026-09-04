// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Locked, Unlocked } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// styles
import styles from './styles'


// pin a controller, or release it to follow the data statistics
export const Auto = ({ slot, auto, setAuto }) => {
    // build the handler
    const click = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // flip the flag
        setAuto(!auto)
        // all done
        return
    }
    // assemble the controllers to hand my {badge}
    const behaviors = {
        onClick: click,
    }

    // a released controller shows an open lock; a pinned one, a closed lock
    const Icon = auto ? Unlocked : Locked
    // the tooltip says what a click does
    const title = auto ? "pin the bounds where they are" : "release the bounds to follow the data"

    // mix my paint
    const paint = styles.auto
    // and render; the badge is a toggle whose pressed state is the flag
    return (
        <Badge size={24} state="enabled" behaviors={behaviors} style={paint}
            title={title} aria-label={`${slot} auto`} aria-pressed={auto}
        >
            <Icon />
        </Badge>
    )
}


// end of file
