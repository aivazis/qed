// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
// locals
// context
import { Context } from './context'


// access to the styling attributes whose names and values depend on the flexbox direction
export default () => {
    // pull the values from the context
    const {
        mainExtent, crossExtent, minExtent, maxExtent, cursor, transform
    } = React.useContext(Context)
    // and make them available
    return { mainExtent, crossExtent, minExtent, maxExtent, cursor, transform }
}


// end of file
