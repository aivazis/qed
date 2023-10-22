// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// provide access to the collection of table repositories
export const useArchives = () => {
    // get the data sources
    const { archives } = React.useContext(Context)
    // and return them
    return archives
}


// end of file
