// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// provide access to the collection of data archives
export const useGetAvailableArchiveTypes = () => {
    // get the data sources
    const { availableArchiveTypes } = React.useContext(Context)
    // and return them
    return availableArchiveTypes
}


// end of file
