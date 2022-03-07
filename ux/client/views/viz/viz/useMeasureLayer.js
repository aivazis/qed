// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the measure layer over this viewport
export const useMeasureLayer = (viewport) => {
    // grab the measure layer flag from context
    const { activeViewport, measureLayer } = React.useContext(Context)
    // and publish it
    return measureLayer[viewport ?? activeViewport]
}


// end of file
