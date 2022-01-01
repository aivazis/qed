// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
// context
import { Context } from './context'


// access to the styling attributes whose names and values depend on the flexbox direction
export default () => {
    // pull the values from the context
    const {
        mainPos, crossPos, mainExtent, crossExtent, minExtent, maxExtent,
        transform,
        cursor,
    } = React.useContext(Context)
    // and make them available
    return {
        mainPos, crossPos, mainExtent, crossExtent, minExtent, maxExtent,
        transform,
        cursor,
    }
}


// end of file
