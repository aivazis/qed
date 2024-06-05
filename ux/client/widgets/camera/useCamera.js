// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Context } from './context'


// publish the current camera state
export const useCamera = () => {
    // grab the camera state and the coordinate transformations
    const { els, camera, cursor, toICS } = React.useContext(Context)
    // and publish it
    return { els, camera, cursor, toICS }
}


// end of file
