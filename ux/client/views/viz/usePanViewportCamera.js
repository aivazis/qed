// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { ViewportContext } from './viewportContext'


// get the viewport position
export const usePanViewportCamera = (viewport) => {
    // grab the position mutator of the viewport camera
    const { setPosition } = React.useContext(ViewportContext)

    // build a function that updates both the viewport and the shared cameras
    const pan = (position) => {
        // and the viewport camera
        setPosition((old) => {
            // if this is not a substantive update
            if (old.x === position.x && old.y === position.y) {
                // bail
                return old
            }
            // otherwise, build the new camera position and return it
            return { ...old, ...position }
        })
        // all done
        return
    }

    // and return it
    return pan
}


// end of file
