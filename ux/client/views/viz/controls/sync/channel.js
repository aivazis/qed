// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useSynced } from '../../../main/useSynced'
import { useSyncAspect } from '../../../main/useSyncAspect'
// components
import { Control } from './control'
import { Toggle } from './toggle'

// the channel sync control
export const Channel = ({ viewport, mark }) => {
    // get the sync state of all the viewports
    const synced = useSynced()
    // get the sync handler factories
    const { toggle, force } = useSyncAspect()
    // render
    return (
        <Control>
            <Toggle
                state={synced[viewport].channel}
                mark={mark}
                toggle={toggle(viewport, "channel")}
                force={force(viewport, "channel")} />
        </Control>
    )
}


// end of file
