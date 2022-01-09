// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// hook to pull the dataset readers out the outlet context
export const useReaders = () => {
    // grab the readers
    const { readers } = React.useContext(VizContext)
    // and return them
    return readers
}


// end of file
