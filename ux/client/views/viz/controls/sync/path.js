// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// hooks
import { useSyncToggleAll } from './useSyncToggleAll'
import { useSyncToggleViewport } from './useSyncToggleViewport'
// components
import { Control } from './control'
import { Toggle } from './toggle'

// the path sync control
export const Path = ({ viewport, view, mark }) => {
    // unpack the view
    const { sync } = useFragment(pathSyncTableFragment, view)
    // build the handler that toggles all viewports
    const { toggle: toggleAll } = useSyncToggleAll()
    // and the single viewport toggle
    const { toggle: toggleViewport } = useSyncToggleViewport()

    // specialize them
    const togglePath = () => {
        // toggle the path entry of the sync table for this viewport
        toggleViewport({ viewport, aspect: "path" })
        // all done
        return
    }
    const toggleAllPath = () => {
        // toggle the path entry of the sync table for this viewport
        toggleAll({ viewport, aspect: "path" })
        // all done
        return
    }

    // render
    return (
        <Control>
            <Toggle
                state={sync.path} mark={mark}
                toggle={togglePath} force={toggleAllPath}
            />
        </Control>
    )
}


const pathSyncTableFragment = graphql`
    fragment pathSyncTableFragment on View {
        sync {
            path
        }
    }
`


// end of file
