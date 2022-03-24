// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// get the origin and shape of the dataset in the given {viewport}
export const useDatasetShape = (viewport) => {
    // grab the active viewport and the set of {views}
    const { views, activeViewport } = React.useContext(Context)
    // extract the dataset information for the given {viewport}
    const { dataset } = views[viewport ?? activeViewport]

    // if there is no registered dataset in {viewport}
    if (dataset === null) {
        // bail
        return { origin: null, shape: null }
    }

    // extract the dataset origin and shape
    const { origin = null, shape = null } = dataset

    // make them available
    return { origin, shape }
}


// end of file
