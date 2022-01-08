// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Locked } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useToggleViewportSync } from './useToggleViewportSync'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Sync = ({ viewport }) => {
    // my event handlers
    const behaviors = {
        // make a handler one that toggles the sync state
        onClick: useToggleViewportSync(viewport)
    }

    // grab my style
    const syncStyle = styles.sync

    // render
    return (
        <Badge size={10} state="available" behaviors={behaviors} style={syncStyle} >
            <Locked style={syncStyle} />
        </Badge>
    )
}


// end of file