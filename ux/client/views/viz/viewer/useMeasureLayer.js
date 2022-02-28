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
export const useMeasureLayer = () => {
    // grab the measure layer flag from context
    const { measureLayer } = React.useContext(Context)
    // and publish it
    return measureLayer
}


// end of file
