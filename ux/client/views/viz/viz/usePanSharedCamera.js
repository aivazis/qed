// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// get the viewport position
export const usePanSharedCamera = () => {
    // grab the sync table and the camera position mutator
    const { camera } = React.useContext(Context)

    // build a controller that updates the shared camera
    const pan = position => {
        // update the shared camera position
        camera.current = { ...camera.current, ...position }
        // all done
        return
    }

    // and return it
    return pan
}


// end of file
