// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useSynced } from '../../viz/useSynced'
import { useSyncAspect } from '../../viz/useSyncAspect'
// components
import { Control } from './control'
import { Toggle } from './toggle'

// the path sync control
export const Path = ({ viewport }) => {
    // get the sync state of all the viewports
    const synced = useSynced()
    // get the sync handler factories
    const { toggle, force } = useSyncAspect()
    // render
    return (
        <Control>
            <Toggle
                state={synced[viewport].path}
                toggle={toggle(viewport, "path")}
                force={force(viewport, "path")} />
        </Control>
    )
}


// end of file
