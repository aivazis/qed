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
export const useGetSharedCameraPostion = () => {
    // grab the value
    const { camera } = React.useContext(VizContext)
    // and return it
    return camera
}


// end of file
