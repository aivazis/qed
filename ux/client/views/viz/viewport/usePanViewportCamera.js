// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// pan the viewport camera
export const usePanViewportCamera = () => {
    // grab the position mutator of the viewport camera
    const { position } = React.useContext(Context)

    // build a controller that updates the viewport camera
    const pan = pos => {
        // update the camera position
        position.current = { ...position.current, ...pos }
        // all done
        return
    }
    // and return it
    return pan
}


// end of file
