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
export const Reset = () => {
    // assemble the controllers to hand my {badge}
    const behaviors = {
    }

    // mix my paint
    const paint = styles.reset
    // and render
    return (
        <Badge size={32} state="enabled" behaviors={behaviors} style={paint} >
            <Icon />
        </Badge>
    )
}


// end of file