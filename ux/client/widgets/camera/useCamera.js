// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Context } from './context'


// publish the current camera state
export const useCamera = () => {
    // grab the camera state, the cursor before and after rounding, and the coordinate
    // transformations
    const { els, camera, cursor, pointer, toICS } = React.useContext(Context)
    // and publish it
    return { els, camera, cursor, pointer, toICS }
}


// end of file
