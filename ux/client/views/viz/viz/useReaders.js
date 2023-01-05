// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// provide access to the collection of data sources
export const useReaders = () => {
    // get the data sources
    const { readers } = React.useContext(Context)
    // and return them
    return readers
}


// end of file
