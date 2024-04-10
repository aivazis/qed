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

// the zoom sync control
export const Zoom = ({ viewport, view, mark }) => {
    // unpack the view
    const { sync } = useFragment(zoomSyncTableFragment, view)
    // build the handler that toggles all viewports
    const { toggle: toggleAll } = useSyncToggleAll()
    // and the single viewport toggle
    const { toggle: toggleViewport } = useSyncToggleViewport()

    // specialize them
    const toggleZoom = () => {
        // toggle the zoom entry of the sync table for this viewport
        toggleViewport({ viewport, aspect: "zoom" })
        // all done
        return
    }
    const toggleAllZoom = () => {
        // toggle the zoom entry of the sync table for this viewport
        toggleAll({ viewport, aspect: "zoom" })
        // all done
        return
    }

    // render
    return (
        <Control>
            <Toggle
                state={sync.zoom} mark={mark}
                toggle={toggleZoom} force={toggleAllZoom}
            />
        </Control>
    )
}


const zoomSyncTableFragment = graphql`
    fragment zoomSyncTableFragment on View {
        sync {
            zoom
        }
    }
`


// end of file
