// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the currently selected dataset
export const useDataset = () => {
    // grab the dataset ref
    const { dataset } = React.useContext(Context)
    // and return its current value
    return dataset.current
}


// end of file
