// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// get the viewport position
export const usePanSharedCamera = (viewport) => {
    // grab the sync table and the camera position mutator
    const { synced, setCamera } = React.useContext(VizContext)

    // make handler for the scroll event
    const pan = (position) => {
        // if the viewport requesting the change is not currently synced to the shared camera
        if (!synced.get(viewport)) {
            // show me
            // console.log("not panning shared camera", viewport)
            // leave everything alone
            return
        }

        // otherwise, update the shared camera
        setCamera((old) => {
            // if this is not a substantive update
            if (old.x === position.x && old.y === position.y) {
                // bail
                return old
            }
            // show me
            console.log("panning shared camera to", position)
            // otherwise, return the new position
            return { ...old, ...position }
        })

        // all done
        return
    }

    // and return it
    return pan
}


// end of file
